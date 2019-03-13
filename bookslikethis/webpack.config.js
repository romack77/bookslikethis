const path = require('path');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');
const UglifyJsPlugin = require('uglifyjs-webpack-plugin');

module.exports = {
    mode: 'development',

    context: __dirname,

    entry: './assets/js/index',

    output: {
        path: path.resolve(__dirname, 'assets/bundles'),
        filename: '[name]-[hash].js',
    },


    plugins: [
        new webpack.DefinePlugin({
            GA_TRACKING_ID: JSON.stringify(process.env.GA_TRACKING_ID)
        }),
        new BundleTracker({
            path: __dirname,
            filename: 'assets/webpack-stats.json'})
    ],

    optimization: {
        minimizer: [new UglifyJsPlugin()],
    },

    module: {
        rules: [
            {
                 test: /\.jsx?$/,
                 exclude: /node_modules/,
                 use: [
                     {
                         loader: 'babel-loader',
                         options: {
                             presets: ['@babel/preset-env', '@babel/preset-react']
                         }
                     }
                 ]
            },
            {
                test: /\.css$/,
                exclude: /node_modules/,
                use: [
                    {
                        loader: 'style-loader',
                    },
                    {
                        loader: 'css-loader',
                        options: {
                           modules: true,
                        },
                    }
                ],
            },
            // Embed small images.
            {
                test: /\.(png|jpg|gif|svg|eot|ttf|woff|woff2)$/,
                loader: 'url-loader',
                options: {
                    limit: 10000,
                },
            },
        ]
    },

    resolve: {
        modules: ['node_modules', 'bower_components'],
        extensions: ['*', '.js', '.jsx']
    },
}