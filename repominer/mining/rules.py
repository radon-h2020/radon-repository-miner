def has_defect_pattern(text: str) -> bool:
    string_pattern = ['error', 'bug', 'fix', 'issu', 'mistake', 'incorrect', 'fault', 'defect', 'flaw']
    return any(word in text.lower() for word in string_pattern)


def has_conditional_pattern(text: str) -> bool:
    string_pattern = ['logic', 'condit', 'boolean']
    return any(word in text.lower() for word in string_pattern)


def has_storage_configuration_pattern(text: str) -> bool:
    string_pattern = ['sql', 'db', 'databas']
    return any(word in text.lower() for word in string_pattern)


def has_file_configuration_pattern(text: str) -> bool:
    string_pattern = ['file', 'permiss']
    return any(word in text.lower() for word in string_pattern)


def has_network_configuration_pattern(text: str) -> bool:
    string_pattern = ['network', 'ip', 'address', 'port', 'tcp', 'dhcp']
    return any(word in text.lower() for word in string_pattern)


def has_user_configuration_pattern(text: str) -> bool:
    string_pattern = ['user', 'usernam', 'password']
    return any(word in text.lower() for word in string_pattern)


def has_cache_configuration_pattern(text: str) -> bool:
    return 'cach' in text.lower()


def has_dependency_pattern(text: str) -> bool:
    string_pattern = ['requir', 'depend', 'relat', 'order', 'sync', 'compat', 'ensur', 'inherit']
    return any(word in text.lower() for word in string_pattern)


def has_documentation_pattern(text: str) -> bool:
    string_pattern = ['doc', 'comment', 'spec', 'licens', 'copyright', 'notic', 'header', 'readm']
    return any(word in text.lower() for word in string_pattern)


def has_idempotency_pattern(text: str) -> bool:
    return 'idempot' in text.lower()


def has_security_pattern(text: str) -> bool:
    string_pattern = ['vul', 'ssl', 'secr', 'authent', 'password', 'secur', 'cve']
    return any(word in text.lower() for word in string_pattern)


def has_service_pattern(text: str) -> bool:
    string_pattern = ['servic', 'server']
    return any(word in text.lower() for word in string_pattern)


def has_syntax_pattern(text: str) -> bool:
    string_pattern = ['compil', 'lint', 'warn', 'typo', 'spell', 'indent', 'regex', 'variabl', 'whitespac']
    return any(word in text.lower() for word in string_pattern)
