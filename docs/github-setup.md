# GitHub Setup Commands

From the folder where you want the project to live:

```bash
mkdir mycelium-learning-lab
cd mycelium-learning-lab
git init
```

Add the starter files, then run:

```bash
git add .
git commit -m "initial research repo setup"
```

Create a new empty repo on GitHub, then connect it:

```bash
git branch -M main
git remote add origin git@github.com:YOUR-USERNAME/mycelium-learning-lab.git
git push -u origin main
```

If using HTTPS instead of SSH:

```bash
git remote add origin https://github.com/YOUR-USERNAME/mycelium-learning-lab.git
git push -u origin main
```
