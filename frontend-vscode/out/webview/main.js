"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = __importDefault(require("react"));
const react_dom_1 = __importDefault(require("react-dom"));
require("./style.scss");
const App = () => {
    return (react_1.default.createElement("div", null,
        react_1.default.createElement("h1", null, "Hello, VS Code Extension!")));
};
react_dom_1.default.render(react_1.default.createElement(App, null), document.getElementById("root"));
