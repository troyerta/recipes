
.PHONY: save
save:
	@echo "====> saving changes"
	@git checkout -b save
	@echo "====> generating SUMMARY.md"
	./rbook
	@echo "====> done"
	@echo "====> adding tracked files"
	@git add -u
	@echo "====> adding new recipes"
	@git add src/*
	@echo "====> committing changes"
	@git commit -m 'Auto-commit on $(shell date)'
	@echo "====> pushing book source to github.com/troyerta/recipes/"
	@git push origin HEAD:master
	@echo "====> resetting workspace"
	@git checkout origin/master
	@git branch -d master
	@git checkout -b master
	@git branch -d save
	@echo "====> Done!"

.PHONY: deploy
deploy: book
	@echo "====> deploying github.com/troyerta/recipes/"
	@git checkout -b temp-deploy-branch
	@echo "====> building a temporary worktree on gh-pages branch"
	@git worktree add ./tmp_book origin/gh-pages
	@echo "====> deleting the old book"
	@rm -rf ./tmp_book/*
	@echo "====> copying over the new book"
	@cp -rp book/* ./tmp_book/
	@echo "====> committing and pushing new book to gh-pages branch"
	@cd ./tmp_book && \
		git checkout -b tmp && \
		git add -A && \
		git commit -m "deployed on $(shell date) by ${USER}" && \
		git push origin HEAD:gh-pages && \
		git checkout origin/gh-pages && \
		git branch -d tmp
	@echo "====> pruning the worktree"
	@rm -rf ./tmp_book
	@git worktree prune
	@echo "====> resetting the workspace"
	@git checkout origin/master
	@git branch -d temp-deploy-branch
	@git branch -d master
	@git checkout -b master
	@echo "====> Done!"