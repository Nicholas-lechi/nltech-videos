SPEC = {
 "series": "60-SECOND JS TIP", "day": 0, "of": 0,
 "title": "Remove duplicates in one line", "folder": "tips",
 "theme": "mint", "next": "More quick tips every day", "seed": 302, "tip": True,
 "steps": [
  {"say": "Need to remove duplicates from an array? Stop writing loops. Here's the one line way.",
   "do": [("open", "dedupe.js", ""), ("type", "const tags = [\"js\", \"ts\", \"js\", \"ts\"];")]},
  {"say": "A Set only stores unique values. So wrap the array in a new Set, then spread it back into an array with three dots.",
   "cap": "A Set only stores unique values. Wrap the array in new Set(), then spread it back into an array with ...",
   "do": [("zoom", True), ("type", "\nconst unique = [...new Set(tags)];\nconsole.log(unique);"), ("zoom", False), ("note", "[...new Set(array)] = no duplicates")]},
  {"say": "Run it. JS and TS, each only once, and the original order is kept.",
   "do": [("term", "node dedupe.js", ["[ 'js', 'ts' ]"]), ("hl", 2, 2)]},
  {"say": "Bonus: a Set's size tells you how many unique values there are, without making a new array.",
   "cap": "Bonus: new Set(tags).size tells you how many unique values there are.",
   "do": [("type", "\nconsole.log(new Set(tags).size);"), ("clear",), ("term", "node dedupe.js", ["[ 'js', 'ts' ]", "2"])]},
  {"say": "Save this for the next time you need it, and follow for a new tip every day.",
   "do": [("wait", 0.4)]},
 ],
}
