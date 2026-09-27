/* alireq_engine.h — C ABI for the Rust hybrid engine.
 *
 * This header is used by the Cython rust_bridge extension to call
 * the Rust engine directly, bypassing ctypes (which crashes on
 * Android ARM64 due to TBI/tagged pointers).
 */
#ifndef ALIREQ_ENGINE_H
#define ALIREQ_ENGINE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Version string — static buffer, do not free */
const char *alireq_engine_version(void);

/* Returns 0 on success, -1 on failure */
int alireq_engine_init(void);
int alireq_engine_self_check(void);

/* Returns 0 = clean, 1 = threat detected, -1 = engine unavailable */
int alireq_threat_scan(void);

/* Returns 0 on success, -1 on failure */
int alireq_harden_ram(void);

/* Frees a string previously returned by the engine (legacy API) */
void alireq_free_string(char *s);

#ifdef __cplusplus
}
#endif

#endif /* ALIREQ_ENGINE_H */
