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
    ],
    hiddenimports=[],
    hookspath=None,
    runtime_hooks=None,
    excludes=None,
)

pyz = PYZ(a.pure)

if options.debug:
    exe = EXE(
        pyz,
        a.scripts,
        name="ChordHand",
        console=True,
        embed_manifest=True,
        exclude_binaries=True,
    )

    coll = COLLECT(exe, a.datas, a.binaries, name="ChordHand")
else:
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



