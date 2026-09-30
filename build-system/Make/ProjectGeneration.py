import json
import os
import re
import shutil
import stat

from BuildEnvironment import is_apple_silicon, call_executable, BuildEnvironment


def remove_directory(path):
    if os.path.isdir(path):
        shutil.rmtree(path)

def generate_xcodeproj(build_environment: BuildEnvironment, disable_extensions, disable_provisioning_profiles, include_release, generate_dsym, bazel_app_arguments, target_name):
    if '/' in target_name:
        app_target_spec = target_name.split('/')[0] + '/' + target_name.split('/')[1] + ':' + target_name.split('/')[1]
        app_target = target_name
        app_target_clean = app_target.replace('/', '_')
    else:
        app_target_spec = '{target}:{target}'.format(target=target_name)
        app_target = target_name
        app_target_clean = app_target.replace('/', '_')

    bazel_generate_arguments = [build_environment.bazel_path]

    xcodeproj_target = '{}_simulator_xcodeproj'.format(app_target_spec) if target_name == 'Telegram' and disable_provisioning_profiles else '{}_xcodeproj'.format(app_target_spec)
    bazel_generate_arguments += ['run', '//{}'.format(xcodeproj_target)]

    if target_name == 'Telegram':
        if disable_extensions:
            bazel_generate_arguments += ['--//{}:disableExtensions'.format(app_target)]
        if disable_provisioning_profiles:
            bazel_generate_arguments += ['--//{}:disableProvisioningProfiles'.format(app_target)]
            bazel_generate_arguments += ['--@build_bazel_rules_swift//swift:copt=-no-warnings-as-errors']
        bazel_generate_arguments += ['--//{}:disableStripping'.format(app_target)]

    project_bazel_arguments = []
    for argument in bazel_app_arguments:
        project_bazel_arguments.append(argument)

    if target_name == 'Telegram':
        if disable_extensions:
            project_bazel_arguments += ['--//{}:disableExtensions'.format(app_target)]
        if disable_provisioning_profiles:
            project_bazel_arguments += ['--//{}:disableProvisioningProfiles'.format(app_target)]
            project_bazel_arguments += ['--@build_bazel_rules_swift//swift:copt=-no-warnings-as-errors']
        project_bazel_arguments += ['--//{}:disableStripping'.format(app_target)]

    project_bazel_arguments += ['--features=-swift.debug_prefix_map']
    project_bazel_arguments += ['--features=swift.emit_swiftsourceinfo']
    
    xcodeproj_bazelrc = os.path.join(build_environment.base_path, 'xcodeproj.bazelrc')
    if os.path.isfile(xcodeproj_bazelrc):
        os.unlink(xcodeproj_bazelrc)
    with open(xcodeproj_bazelrc, 'w') as file:
        for argument in project_bazel_arguments:
            file.write('build ' + argument + '\n')

    xcodeproj_path = '{}.xcodeproj'.format(app_target_spec.replace(':', '/'))
    if target_name == 'Telegram' and disable_provisioning_profiles and os.path.isdir(xcodeproj_path):
        for directory, _, _ in os.walk(xcodeproj_path):
            os.chmod(directory, os.stat(directory).st_mode | stat.S_IWUSR)

    call_executable(bazel_generate_arguments)

    if target_name == 'Telegram' and disable_provisioning_profiles:
        project_file = os.path.join(xcodeproj_path, 'project.pbxproj')
        with open(project_file, 'r') as file:
            project_contents = file.read()
        project_contents, replacements = re.subn(
            r'INFOPLIST_FILE = "\$\(BAZEL_OUT\)/[^";]+/Telegram/rules_xcodeproj/Telegram/Info\.plist";',
            'INFOPLIST_FILE = "";',
            project_contents,
        )
        if replacements != 2:
            raise Exception('Expected two Telegram Info.plist build settings, found {}'.format(replacements))
        os.chmod(project_file, os.stat(project_file).st_mode | stat.S_IWUSR)
        with open(project_file, 'w') as file:
            file.write(project_contents)

    return xcodeproj_path


def generate(build_environment: BuildEnvironment, disable_extensions, disable_provisioning_profiles, include_release, generate_dsym, bazel_app_arguments, target_name) -> str:
    return generate_xcodeproj(build_environment, disable_extensions, disable_provisioning_profiles, include_release, generate_dsym, bazel_app_arguments, target_name)
