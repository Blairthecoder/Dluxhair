# Dlux Hair Salon

Website for Dlux Hair Salon, deployed on Netlify (project: `dlux-hair-salon`).

- Production: https://dlux-hair-salon.netlify.app
- Publish directory: `public/`

## Build

Pages are generated from `tools/build.py` (Python 3, Pillow not required):

```
python3 tools/build.py
```

Edit settings at the top of that file (domain, `BOOKING_URL`, `INDEXABLE`, phone, hours) and the service menus further down, then rebuild and commit `public/`.

- `INDEXABLE = False` keeps every page `noindex` (staging). Set it to `True` at launch, after the placeholder content (About, Reviews, gallery photos) is replaced and `SITE_URL` is the live domain.
