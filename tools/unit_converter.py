"""
Module 24: Unit Converter
Conversion d'unités
"""

class UnitConverter:
    def convert(self, value, from_unit, to_unit):
        conversions = {
            ('km', 'miles'): lambda x: x * 0.621371,
            ('miles', 'km'): lambda x: x * 1.60934,
            ('kg', 'lbs'): lambda x: x * 2.20462,
            ('lbs', 'kg'): lambda x: x * 0.453592,
        }
        key = (from_unit.lower(), to_unit.lower())
        if key in conversions:
            return conversions[key](value)
        return None