# Smart Persian Post Processor

Pipeline:

```text
TextCleaner
→ PersianNormalizer
→ DictionaryEngine
→ Safe Rule Engine
```

Low-risk formatting rules live in:

```text
data/post_processing/safe_rules.json
```

Semantic or vocabulary corrections must remain in the Dictionary Engine.
The processor reports dictionary and formatting replacements separately and
Pipeline writes summary records to `logs/session.log`.
