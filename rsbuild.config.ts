import { defineConfig, loadEnv,  } from '@rsbuild/core';
import { pluginReact } from '@rsbuild/plugin-react';
import { pluginSvgr } from '@rsbuild/plugin-svgr';
const { publicVars } = loadEnv({ prefixes: ['REACT_APP_'] });

export default defineConfig({
    html: {
        template: './public/index.html',
    },
    output: {
        minify: true,
        assetPrefix: './',
    },
    server: {
        host: 'localhost',
        port: 3000,
        strictPort: true,
    },
    plugins: [
        pluginReact(),
        pluginSvgr({ mixedImport: true }),
    ],
    resolve: {
        alias: {
            '@': './src/',
        }
    },
    source: {
        define: publicVars,
    },
});
