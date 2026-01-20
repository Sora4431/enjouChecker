# 🔥 X(Twitter) 炎上リスク診断所

AIがあなたの投稿の炎上リスクを、**学級委員長**、**京都の老舗女将**、**クソリプおじさん**、**特定班**の4つの視点から辛口で診断します。StreamlitとGoogle Gemini APIを使用したWebアプリです。

## 🚀 概要

X（旧Twitter）への投稿予定のテキストを入力すると、AIが炎上リスクをパーセンテージで判定し、各キャラクターからのコメントを表示します。「シェア」ボタンから結果をポストすることも可能です。

## 🌐 ライブデモ

👉 **[こちらから試す](https://enjouchecker.streamlit.app/)**

## 🛠 セットアップ手順

ローカル環境で動作させるための手順です。

### 1. リポジトリのクローン

```bash
git clone https://github.com/[あなたのユーザー名]/[リポジトリ名].git
cd [リポジトリ名]
```

### 2. 依存関係のインストール

Python 3.9以上推奨。

```bash
pip install -r requirements.txt
```

### 3. APIキーの設定 (重要)

このアプリは Google Gemini API を使用します。

1. [Google AI Studio](https://aistudio.google.com/) で APIキーを取得してください。
2. プロジェクトのルートディレクトリに `.streamlit` というフォルダを作成してください。
3. その中に `secrets.toml` というファイルを作成し、以下のように記述してください。
   (※このファイルは機密情報を含むため、Gitにはコミットしないでください)

**.streamlit/secrets.toml**

```toml
GEMINI_API_KEY = "ここに取得したAPIキーを貼り付け"
```

### 4. アプリの起動

```bash
streamlit run app.py
```

ブラウザが自動的に立ち上がり、アプリが表示されます。

## 👨‍💻 開発者情報

Developed by Sora4431
