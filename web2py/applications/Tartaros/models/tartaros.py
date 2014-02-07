# coding: utf8

db = DAL('sqlite://tartaros.sqlite')

# table: submodules
db.define_table('submodules',
                Field('name', unique=True, required=True),
                Field('code', required=True),
)

# table: modules
db.define_table('modules',
                Field('name', unique=True, required=True),
                Field('submodule_id', type='integer', required=True),
)

# table: features
db.define_table('features',
                Field('name', unique=True, required=True),
                Field('submodule_id', type='integer', required=True),
)

# table: user stories
db.define_table('user_stories',
                Field('user_type', required=True),
                Field('action', required=True),
                Field('feature_id', type='integer', required=True),
                Field('module_id', type='integer', required=True),
)

# table: tests
db.define_table('tests',
                Field('name', unique=False, required=True),
                Field('user_story_id', type='integer', required=True),
                Field('results_id', type='integer', required=True),
)

# table: test cases
db.define_table('test_cases',
                Field('name', unique=False, required=True),
                Field('test_id', type='integer', required=True),
                Field('procedure', required=True),
                Field('min_version', required=True),
                Field('test_class', type='integer', required=True),
                Field('active', type='integer', required=True),
                Field('type_id', type='integer', required=True),
)

# table: user types
db.define_table('user_types',
                Field('name', unique=True, required=True),
)

# table: procedure steps
db.define_table('procedure_steps',
                Field('name', type='string', unique=True, required=True),
                Field('function_id', type='integer', unique=False, required=True),
                Field('arguments', type='string', unique=False, required=False),
                Field('verification', type='string', unique=False, required=True),
)

# table: functions
db.define_table('functions',
                Field('function', type='string', unique=True, required=True),
                Field('submodule_id', type='integer', unique=False, required=True)),

# table: test types
db.define_table('test_types',
                Field('name', type='string', unique=True, required=True),
)