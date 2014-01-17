module.exports = function(grunt) {

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        cssmin: {
            combine: {
                files: {
                    'static/stylesheets/style.min.css': [
                        'static/stylesheets/base.css',
                        'static/stylesheets/layout.css',
                        'static/stylesheets/skeleton.css'
                    ]
                }
            }
        }
    })

    grunt.loadNpmTasks('grunt-contrib-cssmin');

    grunt.registerTask('default', 'cssmin');
};
