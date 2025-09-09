const { defineConfig } = require("@vue/cli-service");
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  publicPath: process.env.NODE_ENV === 'production' ? './' : '/',
  
  
  // 配置chainWebpack以进一步处理
  chainWebpack: config => {
    // 配置webpack忽略某些全局变量
    config.externals({
      'MooTools': 'MooTools',
      'Class': 'Class',
      'Events': 'Events',
      '$': 'window.$',
      '$$': 'window.$$'
    });
    
    // 配置webpack忽略MooTools相关的模块解析
    config.resolve.alias.set('mootools-core', false);
  },
  
  // 如果是构建DevTools面板，设置输出目录
  outputDir: process.env.BUILD_TARGET === 'devtools-panel' ? 'chrome-extensions/dist' : 'dist',
  
  // Chrome扩展DevTools面板构建配置
  pages: process.env.BUILD_TARGET === 'devtools-panel' ? {
    'devtools-panel': {
      entry: 'src/chrome-extensions/devtools-panel.js',
      template: 'src/chrome-extensions/devtools-panel.html',
      filename: 'devtools-panel.html',
      title: 'CBG爬虫助手 - DevTools面板'
    }
  } : {
    index: {
      entry: 'src/main.js',
      template: 'public/index.html',
      filename: 'index.html',
      title: 'CBG爬虫助手'
    }
  },
  
  // 自定义webpack配置
  configureWebpack: (config, { isServer } = {}) => {
    // 如果是构建DevTools面板
    if (process.env.BUILD_TARGET === 'devtools-panel') {
      // 设置不压缩
      config.optimization.minimize = false;
      
      return config;
    }
    
    // 默认配置
    return {
      // 配置webpack忽略某些全局变量
      externals: {
        'MooTools': 'window.MooTools',
        'Class': 'window.Class',
        'Events': 'window.Events',
        '$': 'window.$',
        '$$': 'window.$$'
      },
      
      // 配置webpack插件来处理MooTools
      plugins: [
        // 定义全局变量，避免webpack处理MooTools
        new (require('webpack')).DefinePlugin({
          'MooTools': 'window.MooTools',
          'Class': 'window.Class',
          'Events': 'window.Events'
        })
      ]
    };
  }
});
