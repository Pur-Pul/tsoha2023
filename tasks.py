from invoke import task

@task
def start(ctx):
    with ctx.cd("src"):
        ctx.run("flask run")

@task
def lint(ctx):
    ctx.run("pylint src")

@task
def test(ctx):
    ctx.run("coverage run -m pytest src")
    ctx.run("coverage report")