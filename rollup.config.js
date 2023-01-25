import copy from 'rollup-plugin-copy'

export default {
  input: `assets/javascripts/application.js`,
  output: {
    file: `application/static/javascripts/application.js`,
  },
  plugins: [
    copy({
      targets: [
        {
          src: [
            'assets/javascripts/dl-national-map-controller.js',
            'assets/javascripts/filter-checkbox-extension.js'
          ],
          dest: 'application/static/javascripts'
        }
      ]
    })
  ]
}
