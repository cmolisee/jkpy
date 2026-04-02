# CHANGELOG

<!-- version list -->

## v1.1.0 (2026-04-02)

### Features

- Added average story points. removed commented variables from Makefile.
  ([`ef9b4b9`](https://github.com/cmolisee/jkpy/commit/ef9b4b992290ccc7fcd98cd026d28a0d0bc176da))

### Testing

- Fixed datetime issue in show_configurations.
  ([`834f809`](https://github.com/cmolisee/jkpy/commit/834f8094bff46db89aadc29780c426551fffa903))


## v1.0.4 (2026-03-25)

### Testing

- Created tests for back()
  ([`92f314a`](https://github.com/cmolisee/jkpy/commit/92f314a833a5b79a377294c8afbb2043255ae5bb))

- Created tests for edit_configurations
  ([`599fe09`](https://github.com/cmolisee/jkpy/commit/599fe097617e02d8e60c3ba4ab7766bc8d347cc0))

- Created tests for exit_application. updated show_configurations tests to reach 100% coverage for
  callbacks.
  ([`d700790`](https://github.com/cmolisee/jkpy/commit/d7007905a83703da786370a2a8656fe950f31009))

- Created tests for run_application(). Modify .gitignore.
  ([`b56795b`](https://github.com/cmolisee/jkpy/commit/b56795ba9a5db0ce66f3498081b91794df0f199f))

- Introduced tests for show_configurations.
  ([`b6522ce`](https://github.com/cmolisee/jkpy/commit/b6522ceaa0f256674c2141f6b81fbaa22b541e49))

- Updated ruff config to include eof newline. updated typing of **kwargs to Any and removed unused
  type ignores. created tests for setter_prompt().
  ([`785871d`](https://github.com/cmolisee/jkpy/commit/785871d2315a5987a022bc6919dfab5825906233))


## v1.0.3 (2026-03-24)

### Continuous Integration

- Update semanti release commit parsing options.
  ([`391d82c`](https://github.com/cmolisee/jkpy/commit/391d82c1fed74967d2c8369eccf696d7e2a8bcdc))


## v1.0.2 (2026-03-24)

### Chores

- Fix failing test with coroutine invocation.
  ([`9de9b26`](https://github.com/cmolisee/jkpy/commit/9de9b26e08421c9b6c0c6b95902199233e4c177f))


## v1.0.1 (2026-03-23)

### Bug Fixes

- Fixed invocation of coro() to coro as the object is not callable. fixed incorrect access to
  histories attribute in object.
  ([`d829ce9`](https://github.com/cmolisee/jkpy/commit/d829ce91dbaa077fa56a6c46d0da8b90719799d9))


## v1.0.0 (2026-03-11)

- Initial Release
