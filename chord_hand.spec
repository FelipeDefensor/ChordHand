# -*- mode: python ; coding: utf-8 -*-
import argparse

from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true")
options = parser.parse_args()

options = parser.parse_args()

a = Analysis(
    ["./chord_hand/main.py"],
    pathex=[],
    binaries=None,
    datas=[
        ("./README.md", "."),
        ("./chord_hand/settings", "./chord_hand/settings"),
        ("./chord_hand/encoding/projeto_mpb/lex-functions.csv", "./chord_hand/encoding/projeto_mpb"),
        ("./chord_hand/img", "./chord_hand/img"),
    ],
    hiddenimports=['chord_hand.export', 'chord_hand.projeto_mpb'],
    hookspath=None,
    runtime_hooks=None,
    excludes=None,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.datas,
    a.binaries,
    name="ChordHand",
    console=False,
    embed_manifest=True,
)
app = BUNDLE(
    exe,
    name='ChordHand.app',
    version='0.0.1',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'My File Format',
                'CFBundleTypeIconFile': 'MyFileIcon.icns',
                'LSItemContentTypes': ['com.example.myformat'],
                'LSHandlerRank': 'Owner'
                }
            ]
        },
)



