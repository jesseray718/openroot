Hi @Reh1t — welcome aboard, glad to have you picking this up!

One heads-up before you start: our main was recently force-pushed as part of a history cleanup (git filter-repo), so if your clone predates that, it's pointing at old history. To get current:

git fetch origin
git checkout <your-branch>
git rebase origin/main

That avoids the spurious add/add conflicts a stale clone causes — not your problem, ours. Once you're rebased and have something up as a PR, I'll review promptly. The RAG ingestion work is exactly the direction we want. Thanks for contributing!
