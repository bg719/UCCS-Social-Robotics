__version__ = "0.0.0"
__author__ = 'ancient-sentinel'

import json
from spec import *

import simyan.app.scripts.simutils.motion.constants as const
from simyan.app.scripts.simutils.motion.absolute import AbsoluteSequence


class AbsoluteJsonSpecLoader:

    def __init__(self):
        pass

    def load(self, file):
        with open(file, 'r') as infile:
            data = infile.read()

        json_specs = json.loads(data)

        specs = {}
        failed_loads = []
        for key in json_specs:
            try:
                spec = self._create_drawing_spec(key, json_specs[key])
                specs[key] = spec
            except Exception as e:
                print('Error', e.message)
                failed_loads.append(key)

        return specs, failed_loads

    def _create_drawing_spec(self, name, json_spec):
        description = json_spec.get('description') or 'No description.'
        spec = DrawingSpec(name, description)

        for keyword in json_spec.get('keywords') or []:
            spec.keywords.append(keyword)

        if 'sequences' not in json_spec:
            raise InvalidDrawingSpecException('No sequences defined.')

        for json_sequence in json_spec['sequences']:
            sequence = self._create_sequence(json_sequence)
            spec.sequences.append(sequence)

        return spec

    @staticmethod
    def _create_sequence(json_sequence):
        if not json_sequence.get('type') == const.CTYPE_ABSOLUTE:
            raise InvalidDrawingSpecException('Cannot parse non-absolute type sequences')

        effector = json_sequence.get('effector')
        frame = json_sequence.get('frame')
        mask = json_sequence.get('axisMask')
        sequence = AbsoluteSequence(effector, frame, mask)

        default_duration = json_sequence.get('duration')

        for kf in json_sequence['keyframes']:
            type = kf.get('type') or const.KFTYPE_NONE
            effector = kf.get('effector')
            duration = kf.get('duration') or default_duration
            frame = kf.get('frame')
            mask = kf.get('axisMask')
            with_previous = kf.get('withPrevious') or False
            value = kf.get('value')

            if type == 'position':
                added = sequence.next_position_keyframe(value, duration, effector,
                                                        frame, mask, with_previous)
            elif type == 'transform':
                added = sequence.next_transform_keyframe(value, duration, effector,
                                                         frame, mask, with_previous)
            else:
                raise InvalidDrawingSpecException(
                    'Unrecognized keyframe type: {0}'.format(type))

            if not added:
                raise InvalidDrawingSpecException('Failed to add invalid keyframe.')

        return sequence
