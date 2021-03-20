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
        <File name="movement" src="scripts/movement.py" />
        <File name="speech" src="scripts/speech.py" />
        <File name="vision" src="scripts/vision.py" />
        <!-- SIMYAN Utilities Package -->
        <File name="__init__" src="scripts/sim_utils/__init__.py" />
        <File name="__init__" src="scripts/sim_utils/__init__.pyc" />
        <File name="service" src="scripts/sim_utils/service.py" />
        <File name="service" src="scripts/sim_utils/service.pyc" />
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
