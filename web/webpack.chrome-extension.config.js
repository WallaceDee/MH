const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const { CleanWebpackPlugin } = require('clean-webpack-plugin')
const { VueLoaderPlugin } = require('vue-loader')

module.exports = {
  mode: 'development',
  entry: {
    'panel': './src/chrome-extensions/main.js'
  },
  output: {
    path: path.resolve(__dirname, 'chrome-extensions'),
    filename: '[name].js',
    clean: false  // 不要清理整个目录，只清理生成的文件
  },
  module: {
    rules: [
      {
        test: /\.vue$/,
        loader: 'vue-loader'
      },
      {
        test: /\.js$/,
        loader: 'babel-loader',
        exclude: /node_modules/
      },
      {
        test: /\.css$/,
        use: ['vue-style-loader', 'css-loader']
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/,
        type: 'asset/resource'
      }
    ]
  },
  resolve: {
    alias: {
      'vue$': 'vue/dist/vue.esm.js',
      '@': path.resolve(__dirname, 'src')
    },
    extensions: ['*', '.js', '.vue', '.json']
  },
  plugins: [
    // 只清理生成的文件，不清理整个目录
    new CleanWebpackPlugin({
      cleanOnceBeforeBuildPatterns: ['panel.js', 'panel.js.map', 'panel.html'],
      cleanStaleWebpackAssets: false
    }),
    new VueLoaderPlugin(),
    new HtmlWebpackPlugin({
      template: './src/chrome-extensions/devtools-panel.html',
      filename: 'panel.html',
      chunks: ['panel'],
      inject: true
    })
  ],
  devtool: 'source-map',
  optimization: {
    minimize: false // Chrome扩展不需要压缩
  }
}
