name: Update Cloudflare Gateway Rules

on:
  schedule:
  - cron: '0 2 * * *' # Запуск каждый день в два часа ночи
  workflow_dispatch: # Позволяет запускать рабочий процесс вручную

jobs:
  run:
    name: Cloudflare Gateway
    permissions: write-all
    runs-on: ubuntu-latest
    timeout-minutes: 15
    env:
      CF_API_TOKEN: ${{ secrets.CF_API_TOKEN }}
      CF_IDENTIFIER: ${{ secrets.CF_IDENTIFIER }}
      ADLIST_URLS: ${{ vars.ADLIST_URLS }}
      WHITELIST_URLS: ${{ vars.WHITELIST_URLS }}
      DYNAMIC_BLACKLIST: ${{ vars.DYNAMIC_BLACKLIST }}
      DYNAMIC_WHITELIST: ${{ vars.DYNAMIC_WHITELIST }}

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v3 # Использование последней версии
        with:
          fetch-depth: 0

      - name: Install Python
        uses: actions/setup-python@v4 # Использование последней версии
        with:
          python-version: 3.11

      - name: Update Cloudflare Gateway Zero Trust Rules
        run: python -m src run

      - name: Delete workflow runs
        uses: Mattraks/delete-workflow-runs@v2
        with:
          token: ${{ github.token }}
          repository: ${{ github.repository }}
          retain_days: 0
          keep_minimum_runs: 1
