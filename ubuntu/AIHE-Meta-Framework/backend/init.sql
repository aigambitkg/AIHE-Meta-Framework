-- AIHE Meta-Framework Database Initialization
-- This script creates the master data for dimensions and subdimensions

-- Insert the 8 main dimensions
INSERT INTO dimensions (dimension_id, name, description) VALUES
('D1', 'Führung & Governance', 'Entscheidungsstrukturen und ethische Verankerung'),
('D2', 'Strategie & Alignment', 'Zielbild und Ressourcenverankerung'),
('D3', 'Kultur & Veränderung', 'AI-Akzeptanz und Innovationsfähigkeit'),
('D4', 'Kompetenzen & Bildung', 'AI Literacy und Ethikbewusstsein'),
('D5', 'Datenqualität & Ethik', 'Datenmanagement und Fairness & Transparenz'),
('D6', 'Technologieeinsatz', 'Tool-Reife und Innovationszyklus'),
('D7', 'Prozesse & Automatisierung', 'Automatisierung und Monitoring'),
('D8', 'Wirkung & Nachhaltigkeit', 'KPI-Wirkung und ESG-Reflexion')
ON CONFLICT (dimension_id) DO NOTHING;

-- Insert the 16 subdimensions (2 per dimension)
INSERT INTO subdimensions (subdimension_id, parent_dimension_id, name, description, core_question, focus_area) VALUES
-- D1 Subdimensions
('D1.1', 'D1', 'Entscheidungsstruktur', 'Rollen, Gremien und Verantwortlichkeiten für KI-Entscheidungen', 'Wer entscheidet wie über KI?', 'Rollen, Gremien, Verantwortlichkeiten'),
('D1.2', 'D1', 'Ethikverankerung', 'Richtlinien, Risikobewertung und Compliance-Strukturen', 'Leben wir KI-Ethik?', 'Richtlinien, Risikobewertung, Compliance'),

-- D2 Subdimensions
('D2.1', 'D2', 'Zielbild', 'Vision und strategische Ausrichtung für KI-Einsatz', 'Wohin wollen wir mit KI?', 'Vision, strategische Ausrichtung'),
('D2.2', 'D2', 'Ressourcenverankerung', 'Budget, Personal und Kapazitäten für KI-Initiativen', 'Haben wir Budget & Personal?', 'Finanzierung, Kapazitäten'),

-- D3 Subdimensions
('D3.1', 'D3', 'AI-Akzeptanz', 'Einstellung, Ängste und Offenheit gegenüber KI', 'Sind Menschen bereit für KI?', 'Einstellung, Ängste, Offenheit'),
('D3.2', 'D3', 'Innovationsfähigkeit', 'Fehlerkultur, Agilität und Experimentierfreude', 'Können wir experimentieren?', 'Fehlerkultur, Agilität'),

-- D4 Subdimensions
('D4.1', 'D4', 'AI Literacy', 'Grundverständnis und Schulungen zu KI-Technologien', 'Verstehen Menschen KI?', 'Grundverständnis, Schulungen'),
('D4.2', 'D4', 'Ethikbewusstsein', 'Sensibilisierung für KI-Risiken und verantwortungsvoller Umgang', 'Kennen wir KI-Risiken?', 'Sensibilisierung, verantwortungsvoller Umgang'),

-- D5 Subdimensions
('D5.1', 'D5', 'Datenmanagement', 'Datenqualität, Verfügbarkeit und Governance-Strukturen', 'Sind Daten gut genug?', 'Qualität, Verfügbarkeit, Governance'),
('D5.2', 'D5', 'Fairness & Transparenz', 'Bias-Vermeidung und Nachvollziehbarkeit von KI-Entscheidungen', 'Ist unsere KI fair?', 'Bias-Vermeidung, Nachvollziehbarkeit'),

-- D6 Subdimensions
('D6.1', 'D6', 'Tool-Reife', 'KI-Systeme, Plattformen und technische Integration', 'Funktioniert unsere KI-Infrastruktur?', 'Systeme, Plattformen, Integration'),
('D6.2', 'D6', 'Innovationszyklus', 'Time-to-Market und Experimentiergeschwindigkeit', 'Wie schnell entwickeln wir?', 'Time-to-Market, Experimentation'),

-- D7 Subdimensions
('D7.1', 'D7', 'Automatisierung', 'Integration von KI in Geschäftsprozesse und Skalierung', 'Ist KI in Prozesse integriert?', 'Workflow-Integration, Skalierung'),
('D7.2', 'D7', 'Monitoring', 'Performance-Tracking und Alerting für KI-Systeme', 'Überwachen wir KI-Systeme?', 'Performance-Tracking, Alerting'),

-- D8 Subdimensions
('D8.1', 'D8', 'KPI-Wirkung', 'Messung von ROI und Business Impact von KI-Initiativen', 'Was bewirkt unsere KI?', 'Messung, ROI, Business Impact'),
('D8.2', 'D8', 'ESG-Reflexion', 'Umwelt-, Sozial- und Governance-Aspekte von KI-Einsatz', 'Ist KI nachhaltig?', 'Umwelt, Soziales, Governance')
ON CONFLICT (subdimension_id) DO NOTHING;
