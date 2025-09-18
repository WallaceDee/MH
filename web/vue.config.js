const { defineConfig } = require("@vue/cli-service");
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        // target: 'http://xyq.lingtong.xyz/cbg',
        changeOrigin: true
      }
    }
  },
  publicPath: process.env.NODE_ENV === 'production' ? './' : '/',
  
  // 配置webpack以解决MooTools冲突
  configureWebpack: {
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
  },
  
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
  }
});
