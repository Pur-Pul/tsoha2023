from invoke import task

@task
def start(ctx):
    with ctx.cd("src"):
        ctx.run("flask run")

@task
def lint(ctx):
    ctx.run("pylint src")
