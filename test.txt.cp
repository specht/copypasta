Hello, this is a copypasta test.
#{for sample in ["MK", "EK", "EMK"]}
These are the results for sample #{sample}.
#{for threshold in [{"q": 1, "title": "low"}, {"q": 2, "title": "medium"}, {"q": 3, "title": "high"}]}
We have some numbers of #{threshold["title"]} quality for threshold #{threshold["q"]} in sample #{sample}.#{end}
#{end}

#{for x in [1, 2, 3]}
The successor of #{x} is #{x + 1}.
#{end}
