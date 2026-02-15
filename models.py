def new_user(email,password,ref=None):
    return {
        "email":email,
        "password":password,
        "coins":10,
        "ref":ref
    }