#!/usr/bin/env python3
"""Translate every Magium Legacy story scene/choice into French with Argos.

The output retains every YAML node key, ID, check, route and effect. Only
human-readable values stored under `text` are translated. Supports sharding
for parallel GitHub Actions jobs and verification of the entire final pack.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import re
from pathlib import Path

import yaml

CHECKSUM_FILE = 'traduction_manifest.json'


def source_files(source: Path):
    return sorted(x for x in source.glob('*.yaml') if x.name != 'test.yaml')


def logical_structure(obj):
    if isinstance(obj, dict):
        return {key: '<NARRATIVE_TEXT>' if key == 'text' and isinstance(value,str)
                else logical_structure(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [logical_structure(value) for value in obj]
    return obj


def hash_structure(obj):
    return hashlib.sha256(json.dumps(logical_structure(obj), ensure_ascii=False,
                                     sort_keys=True).encode('utf8')).hexdigest()


def traverse(obj, func):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == 'text' and isinstance(value,str):
                obj[key] = func(value)
            else:
                traverse(value, func)
    elif isinstance(obj, list):
        for value in obj:
            traverse(value, func)


def extract_texts(obj):
    results=[]
    def collect(value):
        results.append(value)
        return value
    traverse(copy.deepcopy(obj),collect)
    return results


class Translator:
    def __init__(self, passthrough=False):
        self.cache={}
        self.translated_strings=0
        self.passthrough=passthrough
        if passthrough:
            self.engine=lambda s:s
            return
        from argostranslate import package, translate
        installed=package.get_installed_packages()
        if not any(p.from_code=='en' and p.to_code=='fr' for p in installed):
            package.update_package_index()
            model=next((p for p in package.get_available_packages()
                        if p.from_code=='en' and p.to_code=='fr'),None)
            if model is None:
                raise RuntimeError('English to French Argos model not available')
            package.install_from_path(model.download())
        languages={p.code:p for p in translate.get_installed_languages()}
        self.engine=languages['en'].get_translation(languages['fr']).translate

    def translate(self,value: str) -> str:
        if not value.strip() or value.isspace(): return value
        # Keep exact paragraph breaks, leading spaces, and line separators.
        parts = re.split(r'(\r?\n+)',value)
        finished=[]
        for part in parts:
            if not part or part.startswith('\n') or part.startswith('\r\n'):
                finished.append(part)
                continue
            prefix=part[:len(part)-len(part.lstrip())]
            suffix=part[len(part.rstrip()):]
            content=part.strip()
            if not content or not re.search(r'[A-Za-z]',content):
                finished.append(part)
                continue
            # Split exceptionally long paragraphs; punctuation is preserved.
            items=[]
            if len(content)>1100:
                sentences=re.split(r'(?<=[.!?])\s+(?=[\"“\'\w])',content)
                chunk=''
                for sent in sentences:
                    if chunk and len(chunk)+len(sent)>1000:
                        items.append(chunk);chunk=''
                    chunk=(chunk+' '+sent).strip()
                if chunk:items.append(chunk)
            else:
                items=[content]
            output=[]
            for text in items:
                if text not in self.cache:
                    result=self.engine(text).strip()
                    if not result:raise RuntimeError('Empty translated narrative segment')
                    self.cache[text]=result
                output.append(self.cache[text])
            finished.append(prefix+' '.join(output)+suffix)
        self.translated_strings+=1
        return ''.join(finished)


def translate(source: Path, out: Path, shard: int, shards: int, passthrough:bool):
    filenames=source_files(source)
    if not filenames:raise FileNotFoundError('No English YAML files found in '+str(source))
    relevant=[p for index,p in enumerate(filenames) if index%shards==shard]
    if not relevant:raise RuntimeError('Empty translation shard')
    engine=Translator(passthrough=passthrough)
    out.mkdir(parents=True,exist_ok=True)
    translated=0
    for index,path in enumerate(relevant,1):
        original=yaml.safe_load(path.read_text(encoding='utf8'))
        document=copy.deepcopy(original)
        old_texts=extract_texts(original)
        traverse(document,engine.translate)
        translated_texts=extract_texts(document)
        if len(old_texts)!=len(translated_texts):raise AssertionError('Text count mismatch')
        if hash_structure(original)!=hash_structure(document):
            raise AssertionError('Nontext graph altered in '+path.name)
        dest=out/path.name
        dest.write_text(yaml.safe_dump(document,allow_unicode=True,sort_keys=False,width=1000),encoding='utf8')
        check=yaml.safe_load(dest.read_text(encoding='utf8'))
        if hash_structure(original)!=hash_structure(check):
            raise AssertionError('Reparse graph altered in '+path.name)
        translated+=len(translated_texts)
        print(f'[{index}/{len(relevant)}] {path.name}: {len(translated_texts)} text fields, graph intact',flush=True)
    print(f'COMPLETE shard {shard}/{shards}: {len(relevant)} chapters, {translated} texts',flush=True)


def verify(source:Path,out:Path):
    files=source_files(source)
    if not files:raise FileNotFoundError('English source directory is empty')
    texts=0
    total_chars=0
    for path in files:
        dest=out/path.name
        if not dest.exists():raise FileNotFoundError('Missing translation: '+path.name)
        original=yaml.safe_load(path.read_text(encoding='utf8'))
        translated=yaml.safe_load(dest.read_text(encoding='utf8'))
        if hash_structure(original)!=hash_structure(translated):
            raise AssertionError('Graph integrity failure: '+path.name)
        originals=extract_texts(original);translates=extract_texts(translated)
        if len(originals)!=len(translates):raise AssertionError('Missing narrative fields: '+path.name)
        if not all(isinstance(t,str) and t.strip() for t in translates if t is not None):
            raise AssertionError('Blank translation: '+path.name)
        texts+=len(originals)
        total_chars+=sum(len(x) for x in originals)
    result={'sourceChapters':len(files),'narrativeFields':texts,'sourceCharacters':total_chars,
            'chapters': [p.name for p in files],
            'status':'All narrative text fields translated; logical graph invariant; automatic translation needs literary proofread'}
    (out/CHECKSUM_FILE).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--shard',type=int,default=0)
    p.add_argument('--shards',type=int,default=1)
    p.add_argument('--verify',action='store_true')
    p.add_argument('--passthrough',action='store_true',help='Test graph roundtrip, do not translate')
    args=p.parse_args()
    if args.verify:verify(args.source,args.out)
    else:
        assert 0<=args.shard<args.shards
        translate(args.source,args.out,args.shard,args.shards,args.passthrough)

if __name__=='__main__':main()