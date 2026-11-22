#!/usr/bin/env python3
"""Generate an offline French narration file without changing Magium's graph.

Reads the original CYOA/TLV archive, extracts node text and choice labels,
translates only the content, and writes static/magium-fr.json. All node and edge
identifiers remain those of static/magium.story. It uses Argos Translate while
building the APK; the installed APK needs no translation service or internet.
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
from dataclasses import dataclass
from pathlib import Path

SOURCE = Path("static/magium.story")
TARGET = Path("static/magium-fr.json")


@dataclass(frozen=True)
class Entry:
    idx: int
    kind: int
    cid: bytes
    offset: int
    length: int


def u8(blob: bytes, pos: int) -> tuple[int, int]:
    if pos + 1 > len(blob):
        raise ValueError("Truncated byte field")
    return blob[pos], pos + 1


def u16(blob: bytes, pos: int) -> tuple[int, int]:
    if pos + 2 > len(blob):
        raise ValueError("Truncated u16 field")
    return struct.unpack_from("<H", blob, pos)[0], pos + 2


def u32(blob: bytes, pos: int) -> tuple[int, int]:
    if pos + 4 > len(blob):
        raise ValueError("Truncated u32 field")
    return struct.unpack_from("<I", blob, pos)[0], pos + 4


def skip(blob: bytes, pos: int, length: int) -> int:
    end = pos + length
    if length < 0 or end > len(blob):
        raise ValueError("Invalid CYOA field length")
    return end


def parse_index(data: bytes) -> list[Entry]:
    if len(data) < 22 or data[:4] != b"CYOA":
        raise ValueError("Not a CYOA story file")
    index_offset = struct.unpack_from("<Q", data, 14)[0]
    count, pos = u32(data, index_offset)
    if count > 100000:
        raise ValueError("Suspiciously large CYOA index")
    entries = []
    for idx in range(count):
        kind, pos = u8(data, pos)
        cid = data[pos:skip(data, pos, 3)]
        pos += 3
        if pos + 12 > len(data):
            raise ValueError("Truncated index entry")
        offset, length = struct.unpack_from("<QI", data, pos)
        pos += 12
        if offset + length > len(data):
            raise ValueError("Invalid chunk range")
        entries.append(Entry(idx, kind, cid, offset, length))
    return entries


def chunk_payload(data: bytes, entry: Entry) -> bytes:
    raw = data[entry.offset:entry.offset + entry.length]
    if len(raw) < 9 or raw[0] != entry.kind or raw[1:4] != entry.cid:
        raise ValueError("Bad chunk header")
    flags = raw[4]
    compressed_length = struct.unpack_from("<I", raw, 5)[0]
    pos = 9
    if flags & 1:
        expected_size, pos = u32(raw, pos)
        import zstandard
        result = zstandard.ZstdDecompressor().decompress(
            raw[pos:pos + compressed_length], max_output_size=expected_size
        )
        if len(result) != expected_size:
            raise ValueError("Bad decompressed chunk size")
        return result
    return raw[pos:pos + compressed_length]


def parse_content(blob: bytes) -> str:
    name_len, pos = u16(blob, 0)
    pos = skip(blob, pos, name_len)
    text_len, pos = u32(blob, pos)
    return blob[pos:skip(blob, pos, text_len)].decode("utf-8")


def node_content_ids(blob: bytes) -> list[bytes]:
    pos = 0
    size, pos = u16(blob, pos)
    pos = skip(blob, pos, size)
    size, pos = u8(blob, pos)
    pos = skip(blob, pos, size)
    tags, pos = u16(blob, pos)
    for _ in range(tags):
        size, pos = u8(blob, pos)
        pos = skip(blob, pos, size)
        size, pos = u8(blob, pos)
        pos = skip(blob, pos, size)
    entry_funcs, pos = u16(blob, pos)
    pos = skip(blob, pos, entry_funcs * 12)
    edge_count, pos = u16(blob, pos)
    pos = skip(blob, pos, edge_count * 3)
    translations, pos = u16(blob, pos)
    for _ in range(translations):
        size, pos = u8(blob, pos)
        pos = skip(blob, pos, size + 3)
    seq_count, pos = u16(blob, pos)
    ids: list[bytes] = []
    for _ in range(seq_count):
        pos = skip(blob, pos, 13)  # guard flag, function ID, arg offset, arg length
        ids.append(blob[pos:skip(blob, pos, 3)])
        pos += 3
    return ids


CONTROL = re.compile(r"^\s*(#(?:if|elif|elseif|else|endif|set|define)\b|[{}]\s*$|}\s*else\b)", re.I)
def preserve_format_and_translate(original: str, translate_text) -> str:
    """Never pass conditional expressions or braces to machine translation."""
    translated_lines: list[str] = []
    for line in original.splitlines(keepends=True):
        line_body = line.rstrip("\r\n")
        ending = line[len(line_body):]
        stripped = line_body.strip()
        if not stripped or CONTROL.match(stripped) or not re.search(r'[A-Za-zÀ-ÿ]', stripped):
            translated_lines.append(line)
            continue
        prefix = line_body[:len(line_body) - len(line_body.lstrip())]
        suffix = line_body[len(line_body.rstrip()):]
        result = translate_text(stripped).strip()
        if not result:
            raise ValueError("Translation unexpectedly empty")
        translated_lines.append(prefix + result + suffix + ending)
    translated = "".join(translated_lines)
    original_controls = [line.strip() for line in original.splitlines() if CONTROL.match(line)]
    translated_controls = [line.strip() for line in translated.splitlines() if CONTROL.match(line)]
    if original_controls != translated_controls:
        raise ValueError("A CYOA conditional directive was modified")
    return translated


def load_argos_translator():
    from argostranslate import package, translate
    codes = {(p.from_code, p.to_code) for p in package.get_installed_packages()}
    if ("en", "fr") not in codes:
        print("Installing Argos English -> French model (build-time only)...", flush=True)
        package.update_package_index()
        available = package.get_available_packages()
        model = next((p for p in available if p.from_code == "en" and p.to_code == "fr"), None)
        if model is None:
            raise RuntimeError("No Argos en -> fr translation package available")
        package.install_from_path(model.download())
    languages = {lang.code: lang for lang in translate.get_installed_languages()}
    return languages["en"].get_translation(languages["fr"]).translate


def main() -> None:
    data = SOURCE.read_bytes()
    entries = parse_index(data)
    by_id = {e.cid: e for e in entries}
    content_by_id = {
        e.cid: parse_content(chunk_payload(data, e))
        for e in entries if e.kind == 3
    }
    nodes = [e for e in entries if e.kind == 1]
    if not nodes or not content_by_id:
        raise ValueError("No story nodes or content extracted")

    node_texts: dict[str, str] = {}
    narrative_cids: set[bytes] = set()
    for entry in nodes:
        cids = node_content_ids(chunk_payload(data, entry))
        if not cids:
            raise ValueError("Node without narrative content: " + str(entry.idx))
        if not all(cid in content_by_id for cid in cids):
            raise ValueError("Missing content referenced by node")
        narrative_cids.update(cids)
        node_texts[str(entry.idx)] = "".join(content_by_id[cid] for cid in cids)

    # All remaining content chunks are choice labels in this story format.
    original_choices = sorted({
        v for cid, v in content_by_id.items() if cid not in narrative_cids
    })
    translator = load_argos_translator()
    memo: dict[str, str] = {}
    def tr(text: str) -> str:
        if text not in memo:
            memo[text] = translator(text)
        return memo[text]

    print("Translating", len(nodes), "scenes and",
          len(original_choices), "unique choice labels", flush=True)
    translated_nodes = {}
    for idx, (node_index, story) in enumerate(node_texts.items(), 1):
        translated_nodes[node_index] = preserve_format_and_translate(story, tr)
        print("Translated passage", idx, "/", len(node_texts),
              "(node", node_index + ")", flush=True)
    labels = {english: preserve_format_and_translate(english, tr)
              for english in original_choices}

    # English story starts with the first CYOA node. Extract root-pointer
    # metadata so an unexpected index reorder does not change the opening.
    root_candidates = [e for e in entries if e.kind == 4]
    root_idx = nodes[0].idx
    for metadata in root_candidates:
        ptr = chunk_payload(data, metadata)
        if len(ptr) >= 3 and ptr[:3] in by_id and by_id[ptr[:3]].kind == 1:
            root_idx = by_id[ptr[:3]].idx
            break
    result = {
        "metadata": {
            "language": "fr",
            "origin": "magium.story",
            "sourceSha256": hashlib.sha256(data).hexdigest(),
            "translationMethod": "Argos Translate en->fr at APK build time",
            "passageCount": len(nodes),
            "distinctChoices": len(original_choices),
        },
        "root": translated_nodes[str(root_idx)],
        "nodes": translated_nodes,
        "labels": labels,
    }
    if len(result["nodes"]) != len(nodes):
        raise AssertionError("Scene count changed during translation")
    TARGET.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print("Wrote", TARGET, TARGET.stat().st_size, "bytes", flush=True)


if __name__ == "__main__":
    main()
