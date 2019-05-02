## D2

**D2** is a Python implementaton of the [Dou Dizhu](https://en.wikipedia.org/wiki/Dou_dizhu) deck game.

### How to use

Retrieve the repository, then execute the script to run it under terminal mode:

```
git clone https://github.com/paladin-t/d2.git
cd d2
./d2.py
```

It outputs details beneath every process by default, including your opponents' cards, which is useful for debugging. Set `Utils.isDebug` to `False` to disable the spoiling.

Input the card faces separated by spaces directly to make your put, e.g. `8 9 10 j q k a` for `8♠, 9♣, 10♥, J♦, Q♣, K♥, A♦`, `:)` for 🙂 (black joker), `:D` for 😀 (red joker), etc.

### How it works

The complexity of Dou Dizhu is way far simpler than most chess games. It is possible for the AI to enumerate every valid putting and pick a prior combination according to evaluation and context. The evaluation is pretty rough though, I will leave it to you to explore more possibilities.

Read the only [source](d2.py) file for everything.

### License

[GPLv3](LICENSE)
