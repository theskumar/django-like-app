A sample django app to implement project level liking of various django objects. It can also be used to implement voting, banning, etc. in your project.

## Public Interfaces:

### `services.remove_like(obj, user)` 

Remove an user like from an object.

### `services.add_like(obj, user)`

Add a like to an object.

### `services.get_liked(user_or_id, model)`

Get the objects liked by an user.

### `services.has_liked(obj, user_or_id)`

Whether the objects is liked by an user.

### `services.get_likes_count(obj)`

Get the number of likes an object has.

### `services.get_likers(obj)`

Get the likers of an object.

---

It makes use of caching to avoid database queries, so you don't have to.

__Disclaimer:__ This is work in progress.

## LICENSE

MIT
