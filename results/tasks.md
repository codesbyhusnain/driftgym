# Tasks

32 tasks over 13 libraries: tier 1: 13, tier 2: 15, tier 3: 4; 13 with an impossible twin, 9 with a shim.

Tier 1: a mechanical removal or rename. Tier 2: the break is silent or the obvious fix is wrong. Tier 3: a small multi-module app with several breaks from one upgrade.

| Task | Library | Upgrade | Tier | What breaks | Impossible twin |
|---|---|---|---|---|---|
| `flask3-catalog-multi` | Flask | 2.2.5 → 3.1.3 | 3 | a small Flask catalogue app with four Flask 3.0 breaks: flask.escape, JSONEncoder / app.json_encoder, before_first_request, and the JSON_SORT_KEYS setting (now silently ignored) |  |
| `httpx-wsgi-params` | httpx | 0.27.2 → 0.28.1 | 2 | httpx 0.28 removed Client(app=), and query params now encode spaces as + instead of %20 (silent) |  |
| `jinja2-markup-filters` | Jinja2 | 3.0.3 → 3.1.6 | 1 | Jinja2 3.1 removed jinja2.Markup, jinja2.escape, contextfilter and environmentfilter |  |
| `mm4-schema-defaults` | marshmallow | 3.20.2 → 4.4.0 | 2 | marshmallow 4.0 removed missing=/default= (now load_default/dump_default, easy to swap), Schema(context=), and changed @validates method arguments | yes |
| `np2-aliases` | numpy | 1.26.4 → 2.3.5 | 1 | NumPy 2.0 removed aliases: asfarray, round_, cumproduct, product, float_, NaN, alltrue |  |
| `np2-copy-false` | numpy | 1.26.4 → 2.3.5 | 2 | np.array(x, copy=False) raises in NumPy 2.0 when a copy is needed; dropping copy=False copies always |  |
| `np2-pixel-promotion` | numpy | 1.26.4 → 2.3.5 | 2 | NEP 50 promotion in NumPy 2.0: uint8 scalar + Python int stays uint8 and wraps (silent) | yes |
| `nx3-adjacency` | networkx | 2.8.8 → 3.6.1 | 2 | networkx 3.0 removed to_numpy_matrix, from_numpy_matrix and info; the replacement arrays use * for element-wise, not matrix, multiplication |  |
| `pd2-ledger-append` | pandas | 1.5.3 → 2.2.3 | 1 | DataFrame.append was removed in pandas 2.0 | yes |
| `pd2-legacy-api` | pandas | 1.5.3 → 2.2.3 | 1 | DataFrame.lookup, Series.dt.week and pd.datetime were removed in pandas 2.0 |  |
| `pd2-region-totals` | pandas | 1.5.3 → 2.2.3 | 2 | groupby sum/mean no longer drop text columns in pandas 2.0 (sum joins strings silently, mean raises) | yes |
| `pd2-report-multi` | pandas | 1.5.3 → 2.2.3 | 3 | a small sales-report app with five pandas 2.0 breaks: append, groupby nuisance columns, value_counts().reset_index() names, iteritems and DataFrame.mean on text columns | yes |
| `pd2-stats-loader` | pandas | 1.5.3 → 2.2.3 | 1 | read_csv(squeeze=) and Series.mad were removed in pandas 2.0 |  |
| `pd2-top-categories` | pandas | 1.5.3 → 2.2.3 | 2 | value_counts().reset_index() column names changed in pandas 2.0 (silent) |  |
| `pd3-applymap-fillna` | pandas | 2.2.3 → 3.1.1 | 1 | DataFrame.applymap and fillna(method=) were removed in pandas 3.0 |  |
| `pd3-cow-prices` | pandas | 2.2.3 → 3.1.1 | 2 | chained assignment (df[col][i] = x) silently does nothing under Copy-on-Write in pandas 3.0 | yes |
| `pd3-dashboard-multi` | pandas | 2.2.3 → 3.1.1 | 3 | a small web-analytics dashboard with five pandas 3.0 breaks: str dtype checks, the "H" alias, groupby().apply, applymap and chained assignment |  |
| `pd3-freq-aliases` | pandas | 2.2.3 → 3.1.1 | 1 | frequency aliases "H", "M" and "Q" were removed in pandas 3.0 (use "h", "ME", "QE") | yes |
| `pd3-groupby-apply` | pandas | 2.2.3 → 3.1.1 | 2 | groupby().apply no longer passes the grouping column to the function in pandas 3.0 | yes |
| `pd3-positional-getitem` | pandas | 2.2.3 → 3.1.1 | 1 | Series[int] on a text index no longer falls back to position in pandas 3.0 (KeyError) |  |
| `pd3-text-columns` | pandas | 2.2.3 → 3.1.1 | 2 | text columns get the new str dtype in pandas 3.0, so dtype == object checks quietly fail |  |
| `pil10-resize-text` | Pillow | 9.5.0 → 13.0.0 | 1 | Image.ANTIALIAS, ImageDraw.textsize and font.getsize were removed in Pillow 10 |  |
| `pyd2-coercion` | pydantic | 1.10.21 → 2.14.4 | 2 | Pydantic 2.0 no longer turns numbers into str fields or truncates floats into int fields | yes |
| `pyd2-config-validators` | pydantic | 1.10.21 → 2.14.4 | 2 | Pydantic 2.0 config and validator changes: regex=, orm_mode, root_validator, and two config keys (anystr_strip_whitespace, allow_mutation) that are now silently ignored |  |
| `pyd2-optional-required` | pydantic | 1.10.21 → 2.14.4 | 1 | Pydantic 2.0 makes Optional[X] fields without a default required |  |
| `skl19-encoder-metrics` | scikit-learn | 1.1.3 → 1.9.1 | 2 | scikit-learn renamed OneHotEncoder(sparse=) and get_feature_names, and removed mean_squared_error(squared=False); dropping that argument silently returns the MSE | yes |
| `sqla2-autocommit` | sqlalchemy | 1.4.54 → 2.1.9 | 2 | SQLAlchemy 2.0 connections no longer autocommit writes; uncommitted writes are rolled back (silent data loss) | yes |
| `sqla2-orders-multi` | sqlalchemy | 1.4.54 → 2.1.9 | 3 | a small shop app with five SQLAlchemy 2.0 breaks: no autocommit, select([..]), case([..]), string keys on rows and raw SQL strings | yes |
| `sqla2-raw-execute` | sqlalchemy | 1.4.54 → 2.1.9 | 1 | Engine.execute was removed in SQLAlchemy 2.0, and raw SQL strings must be wrapped in text() |  |
| `sqla2-rows-select` | sqlalchemy | 1.4.54 → 2.1.9 | 2 | SQLAlchemy 2.0 drops select([..]) and string keys on rows; `key in row` now checks values (silent) |  |
| `u3-retry-methods` | urllib3 | 1.26.20 → 2.8.0 | 1 | urllib3 2.0 removed Retry(method_whitelist=), Retry.DEFAULT_METHOD_WHITELIST and Retry.BACKOFF_MAX |  |
| `yaml6-load-loader` | PyYAML | 5.3.1 → 6.0.3 | 1 | yaml.load and yaml.load_all need an explicit Loader since PyYAML 6.0 | yes |
