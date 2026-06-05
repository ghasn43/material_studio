#!/usr/bin/env python
# -*- coding: utf-8 -*-
from category_registry import classify_material_hierarchically

result = classify_material_hierarchically('Oil and gas produced water pre-treatment media for ADNOC operations')
print(f'Category: {result["specific_preset"]}')
print(f'Confidence: {result["confidence_score"]:.0%}')
