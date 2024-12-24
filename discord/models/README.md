# Py-cord Models

This directory contains the pydantic models and types used by py-cord.

## Structure

The models are structured in a way that they mirror the structure of the Discord API.
They are subdivided into the following submodules:

> [!IMPORTANT] Each of the submodules is defined below in order. Submodules may only
> reference in their code classes from the same or lower level submodules. For example,
> `api` may reference classes from `api`, `base` and `types`, but `base` may not
> reference classes from `api`. This is to prevent circular imports and to keep the
> codebase clean and maintainable.

### `types`

Contains python types and dataclasses that are used in the following submodules. These
are used to represent the data in a more pythonic way, and are used to define the
pydantic models.

### `base`

Contains the base models defined in the Discord docs. These are the models you will
often find with a heading like "... Template", and hyperlinks linking to it referring to
it as an "object".

For example, the
[User Template](https://discord.com/developers/docs/resources/user#user-object) is
defined in `base/user.py`.

### `api`

Contains the models that are used to represent the data received and set trough discord
API requests. They represent payloads that are sent and received from the Discord API.

When representing a route, it is preferred to create a single python file for each base
route. If the file may become too large, it is preferred to split it into multiple
files, one for each sub-route. In that case, a submodule with the name of the base route
should be created to hold the sub-routes.

For example, the
[Modify Guild Template](https://discord.com/developers/docs/resources/guild-template#modify-guild-template)
is defined in `api/guild_template.py`.

### `gateway`

Contains the models that are used to represent the data received and sent trough the
Discord Gateway. They represent payloads that are sent and received from the Discord
Gateway.

For example, the [Ready Event](https://discord.com/developers/docs/topics/gateway#hello)
is defined in `gateway/ready.py`.

## Naming

The naming of the models is based on the Discord API documentation. The models are named
after the object they represent in the Discord API documentation. It is generally
preferred to create a new model for each object in the Discord API documentation, even
if the file may only contain a single class, so that the structure keeps a 1:1 mapping
with the Discord API documentation.

## Exporting strategies

The models are exported in the following way:

- The models are exported in the `__init__.py` of their respective submodules.
- Models from the `base` submodule are re-exported in the `__init__.py` of the `modules`
  module.
- The other submodules are re-exported in the `__init__.py` of the `models` module as a
  single import.
- The `models` module is re-exported in the `discord` module.
