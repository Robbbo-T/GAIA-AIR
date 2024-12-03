#### Zip

*   `Ret`: `MakeWide<T>`; `V`: `{u,i}{8,16,32}` \
    <code>Ret **ZipLower**([DW, ] V a, V b)</code>: returns the same bits as
    `InterleaveLower`, but repartitioned into double-width lanes (required in
    order to use this operation with scalars). The optional `DW` (provided for
    consistency with `ZipUpper`) is `RepartitionToWide<DFromV<V>>`.

*   `Ret`: `MakeWide<T>`; `V`: `{u,i}{8,16,32}` \
    <code>Ret **ZipUpper**(DW, V a, V b)</code>: returns the same bits as
    `InterleaveUpper`, but repartitioned into double-width lanes (required in
    order to use this operation with scalars). `DW` is
    `RepartitionToWide<DFromV<V>>`. Only available if `HWY_TARGET !=
    HWY_SCALAR`.

#### Shift within blocks

Ops in this section are only available if `HWY_TARGET != HWY_SCALAR`:

*   `V`: `{u,i}` \
    <code>V **ShiftLeftBytes**&lt;int&gt;([D, ] V)</code>: returns the result of
    shifting independent *blocks* left by `int` bytes \[1, 15\]. The optional
    `D` (provided for consistency with `ShiftRightBytes`) is `DFromV<V>`.

*   <code>V **ShiftLeftLanes**&lt;int&gt;([D, ] V)</code>: returns the result of
    shifting independent *blocks* left by `int` lanes. The optional `D`
    (provided for consistency with `ShiftRightLanes`) is `DFromV<V>`.

*   `V`: `{u,i}` \
    <code>V **ShiftRightBytes**&lt;int&gt;(D, V)</code>: returns the result of
    shifting independent *blocks* right by `int` bytes \[1, 15\], shifting in
    zeros even for partial vectors. `D` is `DFromV<V>`.

*   <code>V **ShiftRightLanes**&lt;int&gt;(D, V)</code>: returns the result of
    shifting independent *blocks* right by `int` lanes, shifting in zeros even
    for partial vectors. `D` is `DFromV<V>`.

*   `V`: `{u,i}` \
    <code>V **CombineShiftRightBytes**&lt;int&gt;(D, V hi, V lo)</code>: returns
    a vector of *blocks* each the result of shifting two concatenated *blocks*
    `hi[i] || lo[i]` right by `int` bytes \[1, 16). `D` is `DFromV<V>`.

*   <code>V **CombineShiftRightLanes**&lt;int&gt;(D, V hi, V lo)</code>: returns
    a vector of *blocks* each the result of shifting two concatenated *blocks*
    `hi[i] || lo[i]` right by `int` lanes \[1, 16/sizeof(T)). `D` is
    `DFromV<V>`.

#### Other fixed-pattern permutations within blocks

*   <code>V **OddEven**(V a, V b)</code>: returns a vector whose odd lanes are
    taken from `a` and the even lanes from `b`.

*   <code>V **DupEven**(V v)</code>: returns `r`, the result of copying even
    lanes to the next higher-indexed lane. For each even lane index `i`,
    `r[i] == v[i]` and `r[i + 1] == v[i]`.

*   <code>V **DupOdd**(V v)</code>: returns `r`, the result of copying odd lanes
    to the previous lower-indexed lane. For each odd lane index `i`, `r[i] ==
    v[i]` and `r[i - 1] == v[i]`. Only available if `HWY_TARGET != HWY_SCALAR`.

Ops in this section are only available if `HWY_TARGET != HWY_SCALAR`:

*   `V`: `{u,i,f}{32}` \
    <code>V **Shuffle1032**(V)</code>: returns *blocks* with 64-bit halves
    swapped.

*   `V`: `{u,i,f}{32}` \
    <code>V **Shuffle0321**(V)</code>: returns *blocks* rotated right (toward
    the lower end) by 32 bits.

*   `V`: `{u,i,f}{32}` \
    <code>V **Shuffle2103**(V)</code>: returns *blocks* rotated left (toward the
    upper end) by 32 bits.

The following are equivalent to `Reverse2` or `Reverse4`, which should be used
instead because they are more general:

*   `V`: `{u,i,f}{32}` \
    <code>V **Shuffle2301**(V)</code>: returns *blocks* with 32-bit halves
    swapped inside 64-bit halves.

*   `V`: `{u,i,f}{64}` \
    <code>V **Shuffle01**(V)</code>: returns *blocks* with 64-bit halves
    swapped.

*   `V`: `{u,i,f}{32}` \
    <code>V **Shuffle0123**(V)</code>: returns *blocks* with lanes in reverse
    order.

### Swizzle

#### Reverse

*   <code>V **Reverse**(D, V a)</code> returns a vector with lanes in reversed
    order (`out[i] == a[Lanes(D()) - 1 - i]`).

*   <code>V **ReverseBlocks**(V v)</code>: returns a vector with blocks in
    reversed order.

The following `ReverseN` must not be called if `Lanes(D()) < N`:

*   <code>V **Reverse2**(D, V a)</code> returns a vector with each group of 2
    contiguous lanes in reversed order (`out[i] == a[i ^ 1]`).

*   <code>V **Reverse4**(D, V a)</code> returns a vector with each group of 4
    contiguous lanes in reversed order (`out[i] == a[i ^ 3]`).

*   <code>V **Reverse8**(D, V a)</code> returns a vector with each group of 8
    contiguous lanes in reversed order (`out[i] == a[i ^ 7]`).

*   `V`: `{u,i}{16,32,64}` \
    <code>V **ReverseLaneBytes**(V a)</code> returns a vector where the bytes of
    each lane are swapped.

*   `V`: `{u,i}` \
    <code>V **ReverseBits**(V a)</code> returns a vector where the bits of each
    lane are reversed.

#### User-specified permutation across blocks

*   <code>V **TableLookupLanes**(V a, unspecified)</code> returns a vector of
    `a[indices[i]]`, where `unspecified` is the return value of
    `SetTableIndices(D, &indices[0])` or `IndicesFromVec`. The indices are not
    limited to blocks, hence this is slower than `TableLookupBytes*` on
    AVX2/AVX-512. Results are implementation-defined unless `0 <= indices[i] <
    Lanes(D())` and `indices[i] <= LimitsMax<TFromD<RebindToUnsigned<D>>>()`.
    Note that the latter condition is only a (potential) limitation for 8-bit
    lanes on the RVV target; otherwise, `Lanes(D()) <= LimitsMax<..>()`.
    `indices` are always integers, even if `V` is a floating-point type.

*   <code>V **TwoTablesLookupLanes**(D d, V a, V b, unspecified)</code> returns
    a vector of `indices[i] < N ? a[indices[i]] : b[indices[i] - N]`, where
    `unspecified` is the return value of `SetTableIndices(d, &indices[0])` or
    `IndicesFromVec` and `N` is equal to `Lanes(d)`. The indices are not limited
    to blocks. Results are implementation-defined unless `0 <= indices[i] < 2 *
    Lanes(d)` and `indices[i] <= LimitsMax<TFromD<RebindToUnsigned<D>>>()`. Note
    that the latter condition is only a (potential) limitation for 8-bit lanes
    on the RVV target; otherwise, `Lanes(D()) <= LimitsMax<..>()`. `indices` are
    always integers, even if `V` is a floating-point type.

*   <code>V **TwoTablesLookupLanes**(V a, V b, unspecified)</code> returns
    `TwoTablesLookupLanes(DFromV<V>(), a, b, indices)`, see above. Note that the
    results of `TwoTablesLookupLanes(d, a, b, indices)` may differ from
    `TwoTablesLookupLanes(a, b, indices)` on RVV/SVE if `Lanes(d) <
    Lanes(DFromV<V>())`.

*   <code>unspecified **IndicesFromVec**(D d, V idx)</code> prepares for
    `TableLookupLanes` with integer indices in `idx`, which must be the same bit
    width as `TFromD<D>` and in the range `[0, 2 * Lanes(d))`, but need not be
    unique.

*   <code>unspecified **SetTableIndices**(D d, TI* idx)</code> prepares for
    `TableLookupLanes` by loading `Lanes(d)` integer indices from `idx`, which
    must be in the range `[0, 2 * Lanes(d))` but need not be unique. The index
    type `TI` must be an integer of the same size as `TFromD<D>`.

*   <code>V **Per4LaneBlockShuffle**&lt;size_t kIdx3, size_t kIdx2, size_t
    kIdx1, size_t kIdx0&gt;(V v)</code> does a per 4-lane block shuffle of `v`
    if `Lanes(DFromV<V>())` is greater than or equal to 4 or a shuffle of the
    full vector if `Lanes(DFromV<V>())` is less than 4.

    `kIdx0`, `kIdx1`, `kIdx2`, and `kIdx3` must all be between 0 and 3.

    Per4LaneBlockShuffle is equivalent to doing a TableLookupLanes with the
    following indices (but Per4LaneBlockShuffle is more efficient than
    TableLookupLanes on some platforms): `{kIdx0, kIdx1, kIdx2, kIdx3, kIdx0+4,
    kIdx1+4, kIdx2+4, kIdx3+4, ...}`

    If `Lanes(DFromV<V>())` is less than 4 and `kIdx0 >= Lanes(DFromV<V>())` is
    true, Per4LaneBlockShuffle returns an unspecified value in the first lane of
    the result. Otherwise, Per4LaneBlockShuffle returns `v[kIdx0]` in the first
    lane of the result.

    If `Lanes(DFromV<V>())` is equal to 2 and `kIdx1 >= 2` is true,
    Per4LaneBlockShuffle returns an unspecified value in the second lane of the
    result. Otherwise, Per4LaneBlockShuffle returns `v[kIdx1]` in the first lane
    of the result.

#### Slide across blocks

*   <code>V **SlideUpLanes**(D d, V v, size_t N)</code>: slides up `v` by `N`
    lanes

    If `N < Lanes(d)` is true, returns a vector with the first (lowest-index)
    `Lanes(d) - N` lanes of `v` shifted up to the upper (highest-index)
    `Lanes(d) - N` lanes of the result vector and the first (lowest-index) `N`
    lanes of the result vector zeroed out.

    In other words, `result[0..N-1]` would be zero, `result[N] = v[0]`,
    `result[N+1] = v[1]`, and so on until `result[Lanes(d)-1] =
    v[Lanes(d)-1-N]`.

    The result of SlideUpLanes is implementation-defined if `N >= Lanes(d)`.

*   <code>V **SlideDownLanes**(D d, V v, size_t N)</code>: slides down `v` by
    `N` lanes

    If `N < Lanes(d)` is true, returns a vector with the last (highest-index)
    `Lanes(d) - N` of `v` shifted down to the first (lowest-index) `Lanes(d) -
    N` lanes of the result vector and the last (highest-index) `N` lanes of the
    result vector zeroed out.

    In other words, `result[0] = v[N]`, `result[1] = v[N + 1]`, and so on until
    `result[Lanes(d)-1-N] = v[Lanes(d)-1]`, and then `result[Lanes(d)-N..N-1]`
    would be zero.

    The results of SlideDownLanes is implementation-defined if `N >= Lanes(d)`.

*   <code>V **Slide1Up**(D d, V v)</code>: slides up `v` by 1 lane

    If `Lanes(d) == 1` is true, returns `Zero(d)`.

    If `Lanes(d) > 1` is true, `Slide1Up(d, v)` is equivalent to
    `SlideUpLanes(d, v, 1)`, but `Slide1Up(d, v)` is more efficient than
    `SlideUpLanes(d, v, 1)` on some platforms.

*   <code>V **Slide1Down**(D d, V v)</code>: slides down `v` by 1 lane

    If `Lanes(d) == 1` is true, returns `Zero(d)`.

    If `Lanes(d) > 1` is true, `Slide1Down(d, v)` is equivalent to
    `SlideDownLanes(d, v, 1)`, but `Slide1Down(d, v)` is more efficient than
    `SlideDownLanes(d, v, 1)` on some platforms.

*   <code>V **SlideUpBlocks**&lt;int kBlocks&gt;(D d, V v)</code> slides up `v`
    by `kBlocks` blocks.

    `kBlocks` must be between 0 and `d.MaxBlocks() - 1`.

    Equivalent to `SlideUpLanes(d, v, kBlocks * (16 / sizeof(TFromD<D>)))`, but
    `SlideUpBlocks<kBlocks>(d, v)` is more efficient than `SlideUpLanes(d, v,
    kBlocks * (16 / sizeof(TFromD<D>)))` on some platforms.

    The results of `SlideUpBlocks<kBlocks>(d, v)` is implementation-defined if
    `kBlocks >= Blocks(d)` is true.

*   <code>V **SlideDownBlocks**&lt;int kBlocks&gt;(D d, V v)</code> slides down
    `v` by `kBlocks` blocks.

    `kBlocks` must be between 0 and `d.MaxBlocks() - 1`.

    Equivalent to `SlideDownLanes(d, v, kBlocks * (16 / sizeof(TFromD<D>)))`,
    but `SlideDownBlocks<kBlocks>(d, v)` is more efficient than
    `SlideDownLanes(d, v, kBlocks * (16 / sizeof(TFromD<D>)))` on some
    platforms.

    The results of `SlideDownBlocks<kBlocks>(d, v)` is implementation-defined if
    `kBlocks >= Blocks(d)` is true.

#### Other fixed-pattern across blocks

*   <code>V **BroadcastLane**&lt;int kLane&gt;(V v)</code>: returns a vector
    with all of the lanes set to `v[kLane]`.

    `kLane` must be in `[0, MaxLanes(DFromV<V>()))`.

*   <code>V **BroadcastBlock**&lt;int kBlock&gt;(V v)</code>: broadcasts the
    16-byte block of vector `v` at index `kBlock` to all of the blocks of the
    result vector if `Lanes(DFromV<V>()) * sizeof(TFromV<V>) > 16` is true.
    Otherwise, if `Lanes(DFromV<V>()) * sizeof(TFromV<V>) <= 16` is true,
    returns `v`.

    `kBlock` must be in `[0, DFromV<V>().MaxBlocks())`.

*   <code>V **OddEvenBlocks**(V a, V b)</code>: returns a vector whose odd
    blocks are taken from `a` and the even blocks from `b`. Returns `b` if the
    vector has no more than one block (i.e. is 128 bits or scalar).

*   <code>V **SwapAdjacentBlocks**(V v)</code>: returns a vector where blocks of
    index `2*i` and `2*i+1` are swapped. Results are undefined for vectors with
    less than two blocks; callers must first check that via `Lanes`. Only
    available if `HWY_TARGET != HWY_SCALAR`.

### Reductions

**Note**: Horizontal operations (across lanes of the same vector) such as
reductions are slower than normal SIMD operations and are typically used outside
critical loops.

The following broadcast the result to all lanes. To obtain a scalar, you can
call `GetLane` on the result, or instead use `Reduce*` below.

*   <code>V **SumOfLanes**(D, V v)</code>: returns the sum of all lanes in each
    lane.
*   <code>V **MinOfLanes**(D, V v)</code>: returns the minimum-valued lane in
    each lane.
*   <code>V **MaxOfLanes**(D, V v)</code>: returns the maximum-valued lane in
    each lane.

The following are equivalent to `GetLane(SumOfLanes(d, v))` etc. but potentially
more efficient on some targets.

*   <code>T **ReduceSum**(D, V v)</code>: returns the sum of all lanes.
*   <code>T **ReduceMin**(D, V v)</code>: returns the minimum of all lanes.
*   <code>T **ReduceMax**(D, V v)</code>: returns the maximum of all lanes.

### Crypto

Ops in this section are only available if `HWY_TARGET != HWY_SCALAR`:

*   `V`: `u8` \
    <code>V **AESRound**(V state, V round_key)</code>: one round of AES
    encryption: `MixColumns(SubBytes(ShiftRows(state))) ^ round_key`. This
    matches x86 AES-NI. The latency is independent of the input values.

*   `V`: `u8` \
    <code>V **AESLastRound**(V state, V round_key)</code>: the last round of AES
    encryption: `SubBytes(ShiftRows(state)) ^ round_key`. This matches x86
    AES-NI. The latency is independent of the input values.

*   `V`: `u8` \
    <code>V **AESRoundInv**(V state, V round_key)</code>: one round of AES
    decryption using the AES Equivalent Inverse Cipher:
    `InvMixColumns(InvShiftRows(InvSubBytes(state))) ^ round_key`. This matches
    x86 AES-NI. The latency is independent of the input values.

*   `V`: `u8` \
    <code>V **AESLastRoundInv**(V state, V round_key)</code>: the last round of
    AES decryption: `InvShiftRows(InvSubBytes(state)) ^ round_key`. This matches
    x86 AES-NI. The latency is independent of the input values.

*   `V`: `u8` \
    <code>V **AESInvMixColumns**(V state)</code>: the InvMixColumns operation of
    the AES decryption algorithm. AESInvMixColumns is used in the key expansion
    step of the AES Equivalent Inverse Cipher algorithm. The latency is
    independent of the input values.

*   `V`: `u8` \
    <code>V **AESKeyGenAssist**&lt;uint8_t kRcon&gt;(V v)</code>: AES key
    generation assist operation

    The AESKeyGenAssist operation is equivalent to doing the following, which
    matches the behavior of the x86 AES-NI AESKEYGENASSIST instruction:
    *  Applying the AES SubBytes operation to each byte of `v`.
    *  Doing a TableLookupBytes operation on each 128-bit block of the
       result of the `SubBytes(v)` operation with the following indices
       (which is broadcast to each 128-bit block in the case of vectors with 32
       or more lanes):
       `{4, 5, 6, 7, 5, 6, 7, 4, 12, 13, 14, 15, 13, 14, 15, 12}`
    *  Doing a bitwise XOR operation with the following vector (where `kRcon`
       is the rounding constant that is the first template argument of the
       AESKeyGenAssist function and where the below vector is broadcasted to
       each 128-bit block in the case of vectors with 32 or more lanes):
       `{0, 0, 0, 0, kRcon, 0, 0, 0, 0, 0, 0, 0, kRcon, 0, 0, 0}`

*   `V`: `u64` \
    <code>V **CLMulLower**(V a, V b)</code>: carryless multiplication of the
    lower 64 bits of each 128-bit block into a 128-bit product. The latency is
    independent of the input values (assuming that is true of normal integer
    multiplication) so this can safely be used in crypto. Applications that wish
    to multiply upper with lower halves can `Shuffle01` one of the operands; on
    x86 that is expected to be latency-neutral.

*   `V`: `u64` \
    <code>V **CLMulUpper**(V a, V b)</code>: as CLMulLower, but multiplies the
    upper 64 bits of each 128-bit block.

## Preprocessor macros

*   `HWY_ALIGN`: Prefix for stack-allocated (i.e. automatic storage duration)
    arrays to ensure they have suitable alignment for Load()/Store(). This is
    specific to `HWY_TARGET` and should only be used inside `HWY_NAMESPACE`.

    Arrays should also only be used for partial (<= 128-bit) vectors, or
    `LoadDup128`, because full vectors may be too large for the stack and should
    be heap-allocated instead (see aligned_allocator.h).

    Example: `HWY_ALIGN float lanes[4];`

*   `HWY_ALIGN_MAX`: as `HWY_ALIGN`, but independent of `HWY_TARGET` and may be
    used outside `HWY_NAMESPACE`.

## Advanced macros

Beware that these macros describe the current target being compiled. Imagine a
test (e.g. sort_test) with SIMD code that also uses dynamic dispatch. There we
must test the macros of the target *we will call*, e.g. via `hwy::HaveFloat64()`
instead of `HWY_HAVE_FLOAT64`, which describes the current target.

*   `HWY_IDE` is 0 except when parsed by IDEs; adding it to conditions such as
    `#if HWY_TARGET != HWY_SCALAR || HWY_IDE` avoids code appearing greyed out.

The following indicate full support for certain lane types and expand to 1 or 0.

*   `HWY_HAVE_INTEGER64`: support for 64-bit signed/unsigned integer lanes.
*   `HWY_HAVE_FLOAT16`: support for 16-bit floating-point lanes.
*   `HWY_HAVE_FLOAT64`: support for double-precision floating-point lanes.

The above were previously known as `HWY_CAP_INTEGER64`, `HWY_CAP_FLOAT16`, and
`HWY_CAP_FLOAT64`, respectively. Those `HWY_CAP_*` names are DEPRECATED.

Even if `HWY_HAVE_FLOAT16` is 0, the following ops generally support `float16_t`
and `bfloat16_t`:

*   `Lanes`, `MaxLanes`
*   `Zero`, `Set`, `Undefined`
*   `BitCast`
*   `Load`, `LoadU`, `LoadN`, `LoadNOr`, `MaskedLoad`, `MaskedLoadOr`
*   `Store`, `StoreU`, `StoreN`, `BlendedStore`
*   `PromoteTo`, `DemoteTo`
*   `PromoteUpperTo`, `PromoteLowerTo`
*   `PromoteEvenTo`, `PromoteOddTo`
*   `Combine`, `InsertLane`, `ZeroExtendVector`
*   `RebindMask`, `FirstN`
*   `IfThenElse`, `IfThenElseZero`, `IfThenZeroElse`

Exception: `UpperHalf`, `PromoteUpperTo`, `PromoteOddTo` and `Combine` are not
supported for the `HWY_SCALAR` target.

`Neg` also supports `float16_t` and `*Demote2To` also supports `bfloat16_t`.

*   `HWY_HAVE_SCALABLE` indicates vector sizes are unknown at compile time, and
    determined by the CPU.

*   `HWY_HAVE_TUPLE` indicates `Vec{2-4}`, `Create{2-4}` and `Get{2-4}` are
    usable. This is already true `#if !HWY_HAVE_SCALABLE`, and for SVE targets,
    and the RVV target when using Clang 16. We anticipate it will also become,
    and then remain, true starting with GCC 14.

*   `HWY_MEM_OPS_MIGHT_FAULT` is 1 iff `MaskedLoad` may trigger a (page) fault
    when attempting to load lanes from unmapped memory, even if the
    corresponding mask element is false. This is the case on ASAN/MSAN builds,
    AMD x86 prior to AVX-512, and Arm NEON. If so, users can prevent faults by
    ensuring memory addresses are aligned to the vector size or at least padded
    (allocation size increased by at least `Lanes(d)`).

*   `HWY_NATIVE_FMA` expands to 1 if the `MulAdd` etc. ops use native fused
    multiply-add for floating-point inputs. Otherwise, `MulAdd(f, m, a)` is
    implemented as `Add(Mul(f, m), a)`. Checking this can be useful for
    increasing the tolerance of expected results (around 1E-5 or 1E-6).

*   `HWY_IS_LITTLE_ENDIAN` expands to 1 on little-endian targets and to 0 on
    big-endian targets.

*   `HWY_IS_BIG_ENDIAN` expands to 1 on big-endian targets and to 0 on
    little-endian targets.

The following were used to signal the maximum number of lanes for certain
operations, but this is no longer necessary (nor possible on SVE/RVV), so they
are DEPRECATED:

*   `HWY_CAP_GE256`: the current target supports vectors of >= 256 bits.
*   `HWY_CAP_GE512`: the current target supports vectors of >= 512 bits.

## Detecting supported targets

`SupportedTargets()` returns a non-cached (re-initialized on each call) bitfield
of the targets supported on the current CPU, detected using CPUID on x86 or
equivalent. This may include targets that are not in `HWY_TARGETS`, and vice
versa. If there is no overlap the binary will likely crash. This can only happen
if:

*   the specified baseline is not supported by the current CPU, which
    contradicts the definition of baseline, so the configuration is invalid; or
*   the baseline does not include the enabled/attainable target(s), which are
    also not supported by the current CPU, and baseline targets (in particular
    `HWY_SCALAR`) were explicitly disabled.

## Advanced configuration macros

The following macros govern which targets to generate. Unless specified
otherwise, they may be defined per translation unit, e.g. to disable >128 bit
vectors in modules that do not benefit from them (if bandwidth-limited or only
called occasionally). This is safe because `HWY_TARGETS` always includes at
least one baseline target which `HWY_EXPORT` can use.

*   `HWY_DISABLE_CACHE_CONTROL` makes the cache-control functions no-ops.
*   `HWY_DISABLE_BMI2_FMA` prevents emitting BMI/BMI2/FMA instructions. This
    allows using AVX2 in VMs that do not support the other instructions, but
    only if defined for all translation units.

The following `*_TARGETS` are zero or more `HWY_Target` bits and can be defined
as an expression, e.g. `-DHWY_DISABLED_TARGETS=(HWY_SSE4|HWY_AVX3)`.

*   `HWY_BROKEN_TARGETS` defaults to a blocklist of known compiler bugs.
    Defining to 0 disables the blocklist.

*   `HWY_DISABLED_TARGETS` defaults to zero. This allows explicitly disabling
    targets without interfering with the blocklist.

*   `HWY_BASELINE_TARGETS` defaults to the set whose predefined macros are
    defined (i.e. those for which the corresponding flag, e.g. -mavx2, was
    passed to the compiler). If specified, this should be the same for all
    translation units, otherwise the safety check in SupportedTargets (that all
    enabled baseline targets are supported) may be inaccurate.

Zero or one of the following macros may be defined to replace the default
policy for selecting `HWY_TARGETS`:

*   `HWY_COMPILE_ONLY_EMU128` selects only `HWY_EMU128`, which avoids intrinsics
    but implements all ops using standard C++.
*   `HWY_COMPILE_ONLY_SCALAR` selects only `HWY_SCALAR`, which implements
    single-lane-only ops using standard C++.
*   `HWY_COMPILE_ONLY_STATIC` selects only `HWY_STATIC_TARGET`, which
    effectively disables dynamic dispatch.
*   `HWY_COMPILE_ALL_ATTAINABLE` selects all attainable targets (i.e. enabled
    and permitted by the compiler, independently of autovectorization), which
    maximizes coverage in tests. Defining `HWY_IS_TEST`, which CMake does for
    the Highway tests, has the same effect.
*   `HWY_SKIP_NON_BEST_BASELINE` compiles all targets at least as good as the
    baseline. This is also the default if nothing is defined. By skipping
    targets older than the baseline, this reduces binary size and may resolve
    compile errors caused by conflicts between dynamic dispatch and -m flags.

At most one `HWY_COMPILE_ONLY_*` may be defined. `HWY_COMPILE_ALL_ATTAINABLE`
may also be defined even if one of `HWY_COMPILE_ONLY_*` is, but will then be
ignored because the flags are tested in the order listed. As an exception,
`HWY_SKIP_NON_BEST_BASELINE` overrides the effect of
`HWY_COMPILE_ALL_ATTAINABLE` and `HWY_IS_TEST`.

## Compiler support

Clang and GCC require opting into SIMD intrinsics, e.g. via `-mavx2` flags.
However, the flag enables AVX2 instructions in the entire translation unit,
which may violate the one-definition rule (that all versions of a function such
as `std::abs` are equivalent, thus the linker may choose any). This can cause
crashes if non-SIMD functions are defined outside of a target-specific
namespace, and the linker happens to choose the AVX2 version, which means it may
be called without verifying AVX2 is indeed supported.

To prevent this problem, we use target-specific attributes introduced via
`#pragma`. Function using SIMD must reside between `HWY_BEFORE_NAMESPACE` and
`HWY_AFTER_NAMESPACE`. Conversely, non-SIMD functions and in particular,
#include of normal or standard library headers must NOT reside between
`HWY_BEFORE_NAMESPACE` and `HWY_AFTER_NAMESPACE`. Alternatively, individual
functions may be prefixed with `HWY_ATTR`, which is more verbose, but ensures
that `#include`-d functions are not covered by target-specific attributes.

WARNING: avoid non-local static objects (namespace scope 'global variables')
between `HWY_BEFORE_NAMESPACE` and `HWY_AFTER_NAMESPACE`. We have observed
crashes on PPC because the compiler seems to have generated an initializer using
PPC10 code to splat a constant to all vector lanes, see #1739. To prevent this,
you can replace static constants with a function returning the desired value.

If you know the SVE vector width and are using static dispatch, you can specify
`-march=armv9-a+sve2-aes -msve-vector-bits=128` and Highway will then use
`HWY_SVE2_128` as the baseline. Similarly, `-march=armv8.2-a+sve
-msve-vector-bits=256` enables the `HWY_SVE_256` specialization for Neoverse V1.
Note that these flags are unnecessary when using dynamic dispatch. Highway will
automatically detect and dispatch to the best available target, including
`HWY_SVE2_128` or `HWY_SVE_256`.

Immediates (compile-time constants) are specified as template arguments to avoid
constant-propagation issues with Clang on Arm.

## Type traits

*   `IsFloat<T>()` returns true if the `T` is a floating-point type.
*   `IsSigned<T>()` returns true if the `T` is a signed or floating-point type.
*   `LimitsMin/Max<T>()` return the smallest/largest value representable in
    integer `T`.
*   `SizeTag<N>` is an empty struct, used to select overloaded functions
    appropriate for `N` bytes.

*   `MakeUnsigned<T>` is an alias for an unsigned type of the same size as `T`.

*   `MakeSigned<T>` is an alias for a signed type of the same size as `T`.

*   `MakeFloat<T>` is an alias for a floating-point type of the same size as
    `T`.

*   `MakeWide<T>` is an alias for a type with twice the size of `T` and the same
    category (unsigned/signed/float).

*   `MakeNarrow<T>` is an alias for a type with half the size of `T` and the
    same category (unsigned/signed/float).

## Memory allocation

`AllocateAligned<T>(items)` returns a unique pointer to newly allocated memory
for `items` elements of POD type `T`. The start address is aligned as required
by `Load/Store`. Furthermore, successive allocations are not congruent modulo a
platform-specific alignment. This helps prevent false dependencies or cache
conflicts. The memory allocation is analogous to using `malloc()` and `free()`
with a `std::unique_ptr` since the returned items are *not* initialized or
default constructed and it is released using `FreeAlignedBytes()` without
calling `~T()`.

`MakeUniqueAligned<T>(Args&&... args)` creates a single object in newly
allocated aligned memory as above but constructed passing the `args` argument to
`T`'s constructor and returning a unique pointer to it. This is analogous to
using `std::make_unique` with `new` but for aligned memory since the object is
constructed and later destructed when the unique pointer is deleted. Typically
this type `T` is a struct containing multiple members with `HWY_ALIGN` or
`HWY_ALIGN_MAX`, or arrays whose lengths are known to be a multiple of the
vector size.

`MakeUniqueAlignedArray<T>(size_t items, Args&&... args)` creates an array of
objects in newly allocated aligned memory as above and constructs every element
of the new array using the passed constructor parameters, returning a unique
pointer to the array. Note that only the first element is guaranteed to be
aligned to the vector size; because there is no padding between elements,
the alignment of the remaining elements depends on the size of `T`.

## Speeding up code for older x86 platforms

Thanks to @dzaima for inspiring this section.

It is possible to improve the performance of your code on older x86 CPUs while
remaining portable to all platforms. These older CPUs might indeed be the ones
for which optimization is most impactful, because modern CPUs are usually faster
and thus likelier to meet performance expectations.

For those without AVX3, preferably avoid `Scatter*`; some algorithms can be
reformulated to use `Gather*` instead. For pre-AVX2, it is also important to
avoid `Gather*`.

It is typically much more efficient to pad arrays and use `Load` instead of
`MaskedLoad` and `Store` instead of `BlendedStore`.

If possible, use signed 8..32 bit types instead of unsigned types for
comparisons and `Min`/`Max`.

Other ops which are considerably more expensive especially on SSSE3, and
preferably avoided if possible: `MulEven`, i32 `Mul`, `Shl`/`Shr`,
`Round`/`Trunc`/`Ceil`/`Floor`, float16 `PromoteTo`/`DemoteTo`, `AESRound`.

Ops which are moderately more expensive on older CPUs: 64-bit
`Abs`/`ShiftRight`/`ConvertTo`, i32->u16 `DemoteTo`, u32->f32 `ConvertTo`,
`Not`, `IfThenElse`, `RotateRight`, `OddEven`, `BroadcastSignBit`.

It is likely difficult to avoid all of these ops (about a fifth of the total).
Apps usually also cannot more efficiently achieve the same result as any op
without using it - this is an explicit design goal of Highway. However,
sometimes it is possible to restructure your code to avoid `Not`, e.g. by
hoisting it outside the SIMD code, or fusing with `AndNot` or `CompressNot`.
