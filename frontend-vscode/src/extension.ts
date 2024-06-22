// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from "vscode";
import * as path from "path";
import * as fs from "fs";

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext): void {
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
		const panel = vscode.window.createWebviewPanel(
			"kiraWebview", // Identifies the type of the webview. Used internally
			"KIRA Webview", // Title of the panel displayed to the user
			vscode.ViewColumn.One, // Editor column to show the new webview panel in.
			{
				// Enable scripts in the webview
				enableScripts: true,

				// Restrict the webview to only loading content from the `out/web` directory
				localResourceRoots: [vscode.Uri.file(path.join(context.extensionPath, "out", "web"))],
			}
		);

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

// This method is called when your extension is deactivated
export function deactivate(): void {
	// intentionally left blank
}
