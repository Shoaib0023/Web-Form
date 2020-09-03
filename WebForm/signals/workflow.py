LEEG = ''
GEMELD = 'm'
AFWACHTING = 'i'
ON_HOLD = 'h'
AFGEHANDELD = 'o'
GESPLITST = 's'
HEROPEND = 'reopened'
BEHANDELING = 'b'
GEANNULEERD = 'a'
VERZOEK_TOT_AFHANDELING = 'closure requested'
INGEPLAND = 'ingepland'
VERZOEK_TOT_HEROPENEN = 'reopen requested'

TE_VERZENDEN = 'ready to send'
VERZONDEN = 'sent'
VERZENDEN_MISLUKT = 'send failed'
AFGEHANDELD_EXTERN = 'done external'

STATUS_CHOICES_API = (
    (GEMELD, 'Gemeld'),
    (AFWACHTING, 'In afwachting van behandeling'),
    (ON_HOLD, 'On hold'),
    (AFGEHANDELD, 'Afgehandeld'),
    (GESPLITST, 'Gesplitst'),
    (HEROPEND, 'Heropend'),
    (BEHANDELING, 'In behandeling'),
    (INGEPLAND, 'Ingepland'),
    (TE_VERZENDEN, 'Te verzenden naar extern systeem'),
    (GEANNULEERD, 'Geannuleerd'),
    (VERZOEK_TOT_AFHANDELING, 'Verzoek tot afhandeling'),
)

STATUS_CHOICES_APP = (
    (VERZONDEN, 'Verzonden naar extern systeem'),
    (VERZENDEN_MISLUKT, 'Verzending naar extern systeem mislukt'),
    (AFGEHANDELD_EXTERN, 'Melding is afgehandeld in extern systeem'),
    (VERZOEK_TOT_HEROPENEN, 'Verzoek tot heropenen'),
)

STATUS_CHOICES = STATUS_CHOICES_API + STATUS_CHOICES_APP
