# Public Release Checklist

Before pushing this repository to public GitHub, verify:

## Security

- [ ] `config.json` is **not** in repository
- [ ] no real API keys (`sk-...`) in code/docs/examples/history
- [ ] no real WeChat `appid` / `appsecret`
- [ ] no token caches (`wechat_token_cache.json`)
- [ ] no debug payload/readback artifacts
- [ ] no production output artifacts under `output/`

## Documentation

- [ ] README explains how to copy `config.example.json` to `config.json`
- [ ] README clearly states this project publishes to **draft box**
- [ ] README includes security disclaimer and key rotation reminder
- [ ] beginner quickstart exists and is tested

## Legal

- [ ] LICENSE file exists and matches your intent
- [ ] third-party assets/fonts/themes are allowed for redistribution
- [ ] removed non-redistributable files if any

## Final verification commands

```bash
# search common sensitive patterns
grep -RInE 'sk-[A-Za-z0-9]{8,}|appsecret|wechat_token_cache|draft-upload-payload|draft-readback' .

# ensure secrets file is absent
test ! -f config.json && echo "config.json not tracked"
```
