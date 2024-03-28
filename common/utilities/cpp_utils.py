import enum
import functools

import qtlib


class ReturnType(enum.Enum):
    ArithmeticReturn = "Arithmetic_return"
    LogReturn = "Log_return"


def to_cpp_pay_frequency(pay_frequency):
    cpp_pay_frequency = qtlib.FREQUENCY.OtherFrequency
    if pay_frequency == qtlib.FREQUENCY.Annual.name:
        cpp_pay_frequency = qtlib.FREQUENCY.Annual
    elif pay_frequency == qtlib.FREQUENCY.Semiannual.name:
        cpp_pay_frequency = qtlib.FREQUENCY.Semiannual
    elif pay_frequency == qtlib.FREQUENCY.Once.name:
        cpp_pay_frequency = qtlib.FREQUENCY.Once
    elif pay_frequency == qtlib.FREQUENCY.Quarterly.name:
        cpp_pay_frequency = qtlib.FREQUENCY.Quarterly
    elif pay_frequency == qtlib.FREQUENCY.Monthly.name:
        cpp_pay_frequency = qtlib.FREQUENCY.Monthly
    elif pay_frequency == qtlib.FREQUENCY.EveryFourthMonth.name:
        cpp_pay_frequency = qtlib.FREQUENCY.EveryFourthMonth
    elif pay_frequency == qtlib.FREQUENCY.Bimonthly.name:
        cpp_pay_frequency = qtlib.FREQUENCY.Bimonthly
    elif pay_frequency == qtlib.FREQUENCY.Weekly.name:
        cpp_pay_frequency = qtlib.FREQUENCY.Weekly
    elif pay_frequency == qtlib.FREQUENCY.Biweekly.name:
        cpp_pay_frequency = qtlib.FREQUENCY.Biweekly
    elif pay_frequency == qtlib.FREQUENCY.Daily.name:
        cpp_pay_frequency = qtlib.FREQUENCY.Daily
    elif pay_frequency == qtlib.FREQUENCY.NoFrequency.name:
        cpp_pay_frequency = qtlib.FREQUENCY.NoFrequency
    elif pay_frequency == qtlib.FREQUENCY.EveryFourthWeek.name:
        cpp_pay_frequency = qtlib.FREQUENCY.EveryFourthWeek
    else:
        pass
    return cpp_pay_frequency


def to_cpp_day_count(day_count):
    if day_count == qtlib.DayCount.ActualActual.name:
        cpp_day_count = qtlib.DayCount.ActualActual
    elif day_count == qtlib.DayCount.Actual360.name:
        cpp_day_count = qtlib.DayCount.Actual360
    elif day_count == qtlib.DayCount.Thirty360.name:
        cpp_day_count = qtlib.DayCount.Thirty360
    elif day_count == qtlib.DayCount.Actual366.name:
        cpp_day_count = qtlib.DayCount.Actual366
    elif day_count == qtlib.DayCount.Actual365F.name:
        cpp_day_count = qtlib.DayCount.Actual365F
    else:
        cpp_day_count = qtlib.DayCount.Actual365
    return cpp_day_count


def to_cpp_bond_type(coupon_type, interest_rate_type):
    bond_type = qtlib.BondType.NonStandardBond
    if coupon_type == qtlib.BondType.ZeroCouponBond.name:
        bond_type = qtlib.BondType.ZeroCouponBond
    elif coupon_type == qtlib.BondType.DiscountBond.name:
        bond_type = qtlib.BondType.DiscountBond
    elif coupon_type == 'CouponBond':
        if interest_rate_type == qtlib.BondType.FixedRateBond.name:
            bond_type = qtlib.BondType.FixedRateBond
        elif interest_rate_type == qtlib.BondType.FloatRateBond.name:
            bond_type = qtlib.BondType.FloatRateBond
    return bond_type


def to_cpp_VaR_type(VaR_type):
    if VaR_type == qtlib.VaRType.Professional.name:
        return qtlib.VaRType.Professional
    elif VaR_type == qtlib.VaRType.Standard.name:
        return qtlib.VaRType.Standard
    else:
        raise Exception(
            "{}, error type of VaR_type, input must be Professional or Standard"
            .format(VaR_type))


@functools.lru_cache(4)
def to_cpp_market(market):
    if market == qtlib.Market.IB.name:
        cpp_market = qtlib.Market.IB
    else:
        cpp_market = qtlib.Market.SSE
    return cpp_market


def to_cpp_mean_hypothesis(mean_hypothesis):
    if mean_hypothesis == qtlib.MeanHypothesis.SimpleMean.name:
        cpp_mean_hypothesis = qtlib.MeanHypothesis.SimpleMean
    elif mean_hypothesis == qtlib.MeanHypothesis.GeoMean.name:
        cpp_mean_hypothesis = qtlib.MeanHypothesis.GeoMean
    else:
        cpp_mean_hypothesis = qtlib.MeanHypothesis.Zero
    return cpp_mean_hypothesis


def to_cpp_volatility_method(volatility_method):
    if volatility_method == qtlib.VolatilityMethod.Grach.name:
        cpp_volatility_method = qtlib.VolatilityMethod.Grach
    elif volatility_method == qtlib.VolatilityMethod.EWMA.name:
        cpp_volatility_method = qtlib.VolatilityMethod.EWMA
    else:
        cpp_volatility_method = qtlib.VolatilityMethod.SMA
    return cpp_volatility_method


def to_cpp_irs_type(irs_type):
    if irs_type == qtlib.SwapType.Receiver.name:
        cpp_irs_type = qtlib.SwapType.Receiver
    else:
        cpp_irs_type = qtlib.SwapType.Payer
    return cpp_irs_type


def to_cpp_business_convention(biz_convention):
    if biz_convention == qtlib.BusinessDayConvention.ModifiedFollowing.name:
        cpp_biz_convention = qtlib.BusinessDayConvention.ModifiedFollowing
    elif biz_convention == qtlib.BusinessDayConvention.Preceding.name:
        cpp_biz_convention = qtlib.BusinessDayConvention.Preceding
    elif biz_convention == qtlib.BusinessDayConvention.ModifiedPreceding.name:
        cpp_biz_convention = qtlib.BusinessDayConvention.ModifiedPreceding
    elif biz_convention == qtlib.BusinessDayConvention.Unadjusted.name:
        cpp_biz_convention = qtlib.BusinessDayConvention.Unadjusted
    elif biz_convention == qtlib.BusinessDayConvention.HalfMonthModifiedFollowing.name:
        cpp_biz_convention = qtlib.BusinessDayConvention.HalfMonthModifiedFollowing
    else:
        cpp_biz_convention = qtlib.BusinessDayConvention.Following
    return cpp_biz_convention


def to_cpp_date_generation_rule(date_generation_rule):
    if date_generation_rule == qtlib.DateGeneration.Forward.name:
        cpp_date_generation_rule = qtlib.DateGeneration.Forward
    elif date_generation_rule == qtlib.DateGeneration.Zero.name:
        cpp_date_generation_rule = qtlib.DateGeneration.Zero
    elif date_generation_rule == qtlib.DateGeneration.ThirdWednesday.name:
        cpp_date_generation_rule = qtlib.DateGeneration.ThirdWednesday
    elif date_generation_rule == qtlib.DateGeneration.Twentieth.name:
        cpp_date_generation_rule = qtlib.DateGeneration.Twentieth
    elif date_generation_rule == qtlib.DateGeneration.TwentiethIMM.name:
        cpp_date_generation_rule = qtlib.DateGeneration.TwentiethIMM
    elif date_generation_rule == qtlib.DateGeneration.OldCDS.name:
        cpp_date_generation_rule = qtlib.DateGeneration.OldCDS
    elif date_generation_rule == qtlib.DateGeneration.CDS.name:
        cpp_date_generation_rule = qtlib.DateGeneration.CDS
    elif date_generation_rule == qtlib.DateGeneration.CDS2015.name:
        cpp_date_generation_rule = qtlib.DateGeneration.CDS2015
    else:
        cpp_date_generation_rule = qtlib.DateGeneration.Backward
    return cpp_date_generation_rule


def to_cpp_interpolation_method(interpolation_method):
    if interpolation_method == qtlib.Interpolation.AreaPreservingQuadratic.name:
        cpp_interpolation_method = qtlib.Interpolation.AreaPreservingQuadratic
    elif interpolation_method == qtlib.Interpolation.ConstantForward.name:
        cpp_interpolation_method = qtlib.Interpolation.ConstantForward
    elif interpolation_method == qtlib.Interpolation.CubicSpline.name:
        cpp_interpolation_method = qtlib.Interpolation.CubicSpline
    elif interpolation_method == qtlib.Interpolation.HermiteSpline.name:
        cpp_interpolation_method = qtlib.Interpolation.HermiteSpline
    elif interpolation_method == qtlib.Interpolation.LinearForward.name:
        cpp_interpolation_method = qtlib.Interpolation.LinearForward
    elif interpolation_method == qtlib.Interpolation.LogLinear.name:
        cpp_interpolation_method = qtlib.Interpolation.LogLinear
    elif interpolation_method == qtlib.Interpolation.QuadraticForward.name:
        cpp_interpolation_method = qtlib.Interpolation.QuadraticForward
    elif interpolation_method == qtlib.Interpolation.StepHigh.name:
        cpp_interpolation_method = qtlib.Interpolation.StepHigh
    elif interpolation_method == qtlib.Interpolation.StepLow.name:
        cpp_interpolation_method = qtlib.Interpolation.StepLow
    else:
        cpp_interpolation_method = qtlib.Interpolation.Linear
    return cpp_interpolation_method
