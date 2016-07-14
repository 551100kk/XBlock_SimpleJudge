from setuptools import setup

setup(
    name='xblock-simplejudge',
    version='0.1',
    description='SimpleJudge XBlock',
    py_modules=['simplejudge'],
    install_requires=['XBlock'],
    entry_points={
        'xblock.v1': [
            'simplejudge = simplejudge:SimpleJudgeBlock',
        ]
    }
)