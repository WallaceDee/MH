module.exports = {
  root: true,
  env: {
    node: true,
    browser: true,
    // 添加Chrome插件环境
    webextensions: true
  },
  extends: [
    'plugin:vue/essential',
    'eslint:recommended'
  ],
  parserOptions: {
    parser: '@babel/eslint-parser'
  },
  rules: {
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    // 忽略Chrome插件相关的未定义变量错误
    'no-undef': 'off',
    // 忽略未使用的变量
    'no-unused-vars': 'warn',
    // 忽略Vue组件命名规则
    'vue/multi-word-component-names': 'off',
    // 忽略v-for和v-if混用规则
    'vue/no-use-v-if-with-v-for': 'off'
  },
  // 添加Chrome插件的全局变量
  globals: {
    chrome: 'readonly',
    browser: 'readonly'
  },
  overrides: [
    {
      files: [
        '**/__tests__/*.{j,t}s?(x)',
        '**/tests/unit/**/*.spec.{j,t}s?(x)'
      ],
      env: {
        jest: true
      }
    }
  ]
}
