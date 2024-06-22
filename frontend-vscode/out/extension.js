"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode = __importStar(require("vscode"));
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
function activate(context) {
    // Use the console to output diagnostic information (console.log) and errors (console.error)
    // This line of code will only be executed once when your extension is activated
    console.log('Congratulations, your extension "kira-ai-agent" is now active!');
    // The command has been defined in the package.json file
    // Now provide the implementation of the command with registerCommand
    // The commandId parameter must match the command field in package.json
    const disposable = vscode.commands.registerCommand("kira-ai-agent.helloWorld", () => {
        // The code you place here will be executed every time your command is executed
        // Display a message box to the user
        vscode.window.showInformationMessage("Hello World from KIRA!");
    });
    context.subscriptions.push(disposable);
    // Register a new command that opens a webview
    const webviewDisposable = vscode.commands.registerCommand("kira-ai-agent.openWebview", () => {
        // Create and show a new webview panel
        const panel = vscode.window.createWebviewPanel("kiraWebview", // Identifies the type of the webview. Used internally
        "KIRA Webview", // Title of the panel displayed to the user
        vscode.ViewColumn.One, // Editor column to show the new webview panel in.
        {
            // Enable scripts in the webview
            enableScripts: true,
            // Restrict the webview to only loading content from the `out/web` directory
            localResourceRoots: [vscode.Uri.file(path.join(context.extensionPath, "out", "web"))],
        });
        // Get path to the resource on disk
        const htmlPath = vscode.Uri.file(path.join(context.extensionPath, "out", "web", "index.html"));
        // And read the HTML content from the file
        fs.readFile(htmlPath.fsPath, "utf8", (err, data) => {
            if (err) {
                console.error("Error loading webview HTML file:", err);
                return;
            }
            // Set the webview's initial html content
            panel.webview.html = data;
        });
    });
    context.subscriptions.push(webviewDisposable);
}
exports.activate = activate;
// This method is called when your extension is deactivated
function deactivate() {
    // intentionally left blank
}
exports.deactivate = deactivate;
