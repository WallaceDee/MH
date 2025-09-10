const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const { CleanWebpackPlugin } = require('clean-webpack-plugin')
const { VueLoaderPlugin } = require('vue-loader')
const CopyWebpackPlugin = require('copy-webpack-plugin')

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
        exclude: /node_modules/,
        options: {
          // 确保按顺序处理文件
          presets: ['@babel/preset-env']
        }
      },
      {
        test: /\.css$/,
        use: ['vue-style-loader', 'css-loader']
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/,
        type: 'asset/resource'
      },
      {
        test: /\.(png|jpe?g|gif|svg|webp)$/i,
        type: 'asset/resource',
        generator: {
          filename: 'assets/images/[name][ext]'
        }
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
    // 复制public/libs目录到输出目录
    new CopyWebpackPlugin({
      patterns: [
        {
          from: 'public/libs',
          to: 'libs'
        },
        {
          from: 'public/assets',
          to: 'assets'
        }
      ]
    }),
    new HtmlWebpackPlugin({
      template: './src/chrome-extensions/devtools-panel.html',
      filename: 'panel.html',
      chunks: ['panel'],
      inject: true
    })
  ],
  devtool: 'source-map',
  optimization: {
    minimize: false, // Chrome扩展不需要压缩
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        // 确保基础库按顺序加载
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
          priority: 10
        },
        // 公共库
        common: {
          name: 'common',
          minChunks: 2,
          chunks: 'all',
          priority: 5
        }
      }
    }
  }
}
