<?xml version="1.0" encoding="UTF-8" ?>
<Package name="simyan" format_version="4">
    <Manifest src="manifest.xml" />
    <BehaviorDescriptions>
        <BehaviorDescription name="behavior" src="." xar="behavior.xar" />
    </BehaviorDescriptions>
    <Dialogs />
    <Resources>
        <File name="icon" src="icon.png" />
        <!-- SIMYAN Core SDK -->
        <File name="simyan" src="scripts/simyan.py" />
        <File name="simyan" src="scripts/simyan.pyc" />
        <File name="movement" src="scripts/movement.py" />
        <File name="movement" src="scripts/movement.pyc" />
        <File name="speech" src="scripts/speech.py" />
        <File name="speech" src="scripts/speech.pyc" />
        <File name="vision" src="scripts/vision.py" />
        <File name="vision" src="scripts/vision.pyc" />
        <!-- SIMYAN Utilities Package -->
        <File name="__init__" src="scripts/simutils/__init__.py" />
        <File name="__init__" src="scripts/simutils/__init__.pyc" />
        <File name="service" src="scripts/simutils/service.py" />
        <File name="service" src="scripts/simutils/service.pyc" />
        <File name="speech" src="scripts/simutils/speech.py" />
        <File name="speech" src="scripts/simutils/speech.pyc" />
        <File name="_context" src="scripts/simutils/motion/_context.py" />
        <File name="_context" src="scripts/simutils/motion/_context.pyc" />
        <File name="_handler" src="scripts/simutils/motion/_handler.py" />
        <File name="_handler" src="scripts/simutils/motion/_handler.pyc" />
        <File name="_sequence" src="scripts/simutils/motion/_sequence.py" />
        <File name="_sequence" src="scripts/simutils/motion/_sequence.pyc" />
        <File name="absolute" src="scripts/simutils/motion/absolute.py" />
        <File name="absolute" src="scripts/simutils/motion/absolute.pyc" />
        <File name="codes" src="scripts/simutils/motion/codes.py" />
        <File name="codes" src="scripts/simutils/motion/codes.pyc" />
        <File name="constants" src="scripts/simutils/motion/constants.py" />
        <File name="constants" src="scripts/simutils/motion/constants.pyc" />
        <File name="models" src="scripts/simutils/motion/models.py" />
        <File name="models" src="scripts/simutils/motion/models.pyc" />
        <File name="planar" src="scripts/simutils/motion/planar.py" />
        <File name="planar" src="scripts/simutils/motion/planar.pyc" />
        <File name="preparation" src="scripts/simutils/motion/preparation.py" />
        <File name="preparation" src="scripts/simutils/motion/preparation.pyc" />
        <File name="utils" src="scripts/simutils/motion/utils.py" />
        <File name="utils" src="scripts/simutils/motion/utils.pyc" />
        <!-- Studio Tool Kit Package -->
        <File name="__init__" src="scripts/stk/__init__.py" />
        <File name="__init__" src="scripts/stk/__init__.pyc" />
        <File name="events" src="scripts/stk/events.py" />
        <File name="events" src="scripts/stk/events.pyc" />
        <File name="logging" src="scripts/stk/logging.py" />
        <File name="logging" src="scripts/stk/logging.pyc" />
        <File name="runner" src="scripts/stk/runner.py" />
        <File name="runner" src="scripts/stk/runner.pyc" />
        <File name="services" src="scripts/stk/services.py" />
        <File name="services" src="scripts/stk/services.pyc" />
    </Resources>
    <Topics />
    <IgnoredPaths>
        <Path src=".metadata" />
    </IgnoredPaths>
</Package>
