Hi @Reh1t — thank you for putting this PR together, glad to have you contributing to OpenRoot!

One heads-up before review: our main was recently force-pushed as part of a history cleanup (git filter-repo), so your clone predates the new history and the PR may show some spurious add/add conflicts. That's on our side, not anything you did.

To rebase onto the new main:

git fetch origin
git checkout <your-branch>
git rebase origin/main

Once you've rebased and pushed, I'll review promptly — the RAG ingestion work is exactly the direction we want. Thanks again!
