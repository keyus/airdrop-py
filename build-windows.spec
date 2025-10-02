# -*- mode: python ; coding: utf-8 -*-


block_cipher = None
added_files = [
    ('.\\dist', 'dist'),
    ('.\\src_py\\config','config'),
]

a = Analysis(['.\\src_py\\main.py'],
             pathex=['.\\dist'],
             binaries=[],
             datas=added_files,
             hiddenimports=['clr'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='airdrop tools',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,       # 禁用UPX压缩，防止被杀毒软件误报
          upx_exclude=[],
          uac_admin=True,  # 添加UAC管理员请求
          uac_uiaccess=False,
          icon='.\\icons\\icon.ico',
          runtime_tmpdir=None,
          console=False,
          manifest="app.manifest",
          disable_windowed_traceback=False,
          target_arch='64bit',
          codesign_identity=None,
          entitlements_file=None )