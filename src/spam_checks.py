from spam_handling import *


@spam_check(name="Spam test 1", sites=(False, set(("codegolf.stackexchange.com",))), max_rep=10)
def spam_test_1(post):
    if len(post.body) > 100:
        return "Post length is greater than 100"
    else:
        return ""


regex_spam_check(r"\bvashikaran\Wspecialist\b", name="Bad keyword in %s", sites=(True, set("")), max_rep=50, max_score=2, body=True)
