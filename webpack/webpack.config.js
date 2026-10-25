const path = require("path");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const TerserPlugin = require("terser-webpack-plugin");

const mode = process.env.mode || "production";
const prodMode = mode == "production";

module.exports = {
  mode: mode,
  context: path.resolve(__dirname, "app"),
  entry: {
    "senaite.dashboard": "./index.js"
  },
  output: {
    filename: "[name].js",
    path: path.resolve(
      __dirname, "../src/senaite/dashboard/browser/static")
  },
  resolve: {
    extensions: [".js", ".jsx"],
    alias: {
      "react/jsx-runtime": path.resolve(
        __dirname, "app/shims/jsx-runtime.js")
    }
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: [/node_modules/],
        use: ["babel-loader"]
      }, {
        test: /\.(css|scss)$/,
        use: [MiniCssExtractPlugin.loader, "css-loader", "sass-loader"]
      }
    ]
  },
  devtool: prodMode ? false : "eval-cheap-module-source-map",
  optimization: {
    minimize: prodMode,
    minimizer: [
      new TerserPlugin({
        extractComments: false,
        terserOptions: {format: {comments: false}}
      })
    ]
  },
  plugins: [
    new MiniCssExtractPlugin({filename: "[name].css"})
  ],
  externals: {
    // The one React of the page, provided by senaite.core
    react: "React",
    "react-dom": "ReactDOM",
    "react-dom/client": "ReactDOM"
  }
};
