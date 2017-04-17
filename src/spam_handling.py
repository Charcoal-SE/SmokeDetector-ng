# vim: set filetype=python tabstop=4 shiftwidth=4 expandtab:

import re

_spam_checks = []


def spam_check(name="Missingno.", all=False, sites=set(), max_rep=10, max_score=1):
    def decorator(func):
        def check(post):
            if post.owner_rep <= max_rep and post.post_score <= max_score and all == (post.post_site not in sites):
                reason = func(post)

                if reason:
                    return True, ["%s: %s" % (name, reason)]
                else:
                    return False, ""
            else:
                return False, ""

        _spam_checks.append(check)
        return check

    return decorator


def regex_spam_check(regex, name="Missingno.", sites=(False, set()), max_rep=10, max_score=1, **types):
    compiled_regex = re.compile(regex)

    @spam_check(name=name, sites=sites, max_rep=max_rep, max_score=1)
    def check(post):
        reasons = []

        for key, value in types.items():
            if value:
                match = re.search(compiled_regex, post[key])

                if match:
                    reasons.append("%s: %r" % (key, match))

        return ",".join(reasons)

    return check


def check_if_spam(post):
    is_spam = False
    reasons = []

    for check in _spam_checks:
        result, reason = check(post)

        if not is_spam and result:
            is_spam = True

        reasons.extend(reason)

    return is_spam, reasons
